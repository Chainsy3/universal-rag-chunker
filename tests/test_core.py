import contextlib
import copy
import io
import json
from pathlib import Path
import random
import tempfile
import unittest
from unittest.mock import patch

from universal_rag_chunker import Config, Pipeline, Registry
from universal_rag_chunker.cli import main
from universal_rag_chunker.exporters import export
from universal_rag_chunker.models import DocumentIR
from universal_rag_chunker.pipeline import ParseError
from universal_rag_chunker.plugins import ExampleMetadataPlugin
from universal_rag_chunker.validators import ValidationError, validate_chunks, validate_ir


class CoreTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)

    def run_source(self, text, suffix='.md', **options):
        source = self.root / ('sample' + suffix)
        source.write_bytes(text.encode('utf-8'))
        return Pipeline().run(source, Config(**options))

    def cli(self, args):
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            return main(args)

    def test_exact_crlf_unicode_offsets(self):
        text = '# 使用\r\nHello 世界😀。\r\n\r\n结束'
        result = self.run_source(text)
        self.assertEqual(''.join(b.text for b in result.document.blocks), text)
        for block in result.document.blocks:
            self.assertEqual(text[block.locator['start']:block.locator['end']], block.text)
        self.assertEqual(result.report['coverage'], 1)

    def test_fenced_heading_not_heading(self):
        result = self.run_source('# Top\n```python\n# code\nprint(1)\n```\n## Child\ntext')
        self.assertEqual([b.attributes['title'] for b in result.document.blocks if b.type == 'heading'], ['Top','Child'])
        self.assertEqual(len([b for b in result.document.blocks if b.type == 'code']), 1)
        self.assertEqual(result.chunks[-1].heading_path[-1]['title'], 'Child')

    def test_no_domain_filtering(self):
        text = 'ISBN 中国铁道出版社\n\\frac{1}{2}\n![](diagram.png)\nEnglish scientific formula x = 2.\n42\n'
        result = self.run_source(text)
        self.assertEqual(''.join(c.text for c in result.chunks), text)

    def test_deterministic_and_export_options_excluded(self):
        text = '# Same\nRepeated paragraph.\n'
        first = self.run_source(text)
        second = self.run_source(text, format='json', include_ir=False)
        self.assertEqual(first.document.to_dict(), second.document.to_dict())
        self.assertEqual([c.to_dict() for c in first.chunks], [c.to_dict() for c in second.chunks])

    def test_ir_round_trip(self):
        result = self.run_source('plain text', '.txt')
        document = DocumentIR.from_dict(json.loads(json.dumps(result.document.to_dict())))
        validate_ir(document)
        self.assertEqual(document, result.document)

    def test_sizes_overlap_progress_randomized(self):
        rng = random.Random(7)
        for strategy in ('fixed','recursive'):
            for size in (1,2,7,30):
                text = ''.join(rng.choice('ab中😀。\n ') for _ in range(150))
                result = self.run_source(text, '.txt', strategy=strategy, max_characters=size,
                                         minimum_characters=0, overlap_characters=size-1)
                self.assertTrue(all(len(c.text) <= size for c in result.chunks))
                self.assertEqual(result.report['coverage'],1)

    def test_long_code_and_unpunctuated(self):
        for text in ('甲'*200, '```\n'+'x'*200+'\n```'):
            result = self.run_source(text,max_characters=20,minimum_characters=5,overlap_characters=3)
            self.assertTrue(all(len(c.text)<=20 for c in result.chunks))
            self.assertTrue(any(c.metadata['core.continuation'] for c in result.chunks))

    def test_empty_and_whitespace_rejected(self):
        for text in ('',' \r\n\t'):
            with self.assertRaisesRegex(ValidationError,'EMPTY_DOCUMENT'):
                self.run_source(text)

    def test_bad_encoding_is_parse_error(self):
        source = self.root/'bad.txt'
        source.write_bytes(b'\xff')
        with self.assertRaises(ParseError):
            Pipeline().run(source)

    def test_invalid_configuration(self):
        for values in ({'max_characters':0}, {'overlap_characters':1200}, {'minimum_characters':-1},
                       {'max_characters':True}, {'schema_version':'2.0'}, {'plugins':('a','a')}):
            with self.assertRaises(ValueError):
                Config(**values)
        path=self.root/'config.toml'
        path.write_text('[chunking]\nmax_charcters=10',encoding='utf-8')
        with self.assertRaises(ValueError):
            Config.load(path)

    def test_config_precedence(self):
        path=self.root/'config.toml'
        path.write_text('[chunking]\nmax_characters=300',encoding='utf-8')
        self.assertEqual(Config.load(path,max_characters=400).max_characters,400)

    def test_unknown_components_and_incompatible_parser(self):
        for options in ({'strategy':'typo'},{'parser':'text'},{'plugins':('typo',)}):
            with self.assertRaises(ValueError):
                self.run_source('hello',**options)
        registry=Registry()
        with self.assertRaises(ValueError):
            registry.register('plugins',ExampleMetadataPlugin())

    def test_opt_in_plugin(self):
        default=self.run_source('hello')
        enhanced=self.run_source('hello',plugins=('example_metadata',))
        self.assertNotIn('example.source_name',default.chunks[0].metadata)
        self.assertEqual(enhanced.chunks[0].metadata['example.source_name'],'sample.md')

    def test_bad_plugin_has_context(self):
        class Bad(ExampleMetadataPlugin):
            name='bad'
            def enrich(self,document,drafts,config):
                raise RuntimeError('broken')
        registry=Registry()
        registry.register('plugins',Bad())
        source=self.root/'sample.txt'
        source.write_text('hello',encoding='utf-8')
        with self.assertRaisesRegex(ValidationError,'bad.enrich'):
            Pipeline(registry).run(source,Config(plugins=('bad',)))

    def test_tampering_detected(self):
        result=self.run_source('# Title\nhello')
        for mutate in (lambda c:setattr(c,'text','invented'),
                       lambda c:c.size.update(characters=999),
                       lambda c:c.source_spans[0].update(end=999),
                       lambda c:setattr(c,'schema_version','9')):
            chunks=copy.deepcopy(result.chunks)
            mutate(chunks[0])
            with self.assertRaises(ValidationError):
                validate_chunks(result.document,chunks,1200)
        with self.assertRaises(ValidationError):
            validate_chunks(result.document,[],1200)

    def test_export_json_and_jsonl_reload(self):
        for format in ('json','jsonl'):
            result=self.run_source('# Title\nhello',format=format)
            output=self.root/format
            manifest=export(result,output)
            self.assertNotIn(str(self.root),json.dumps(manifest))
            self.assertEqual(self.cli(['validate',str(output/'document.ir.json'),'--chunks',str(output/('chunks.'+format))]),0)
            self.assertEqual(self.cli(['inspect',str(output/'document.ir.json')]),0)
            with self.assertRaises(FileExistsError):
                export(result,output)
            export(result,output,overwrite=True)

    def test_publish_failure_restores_previous_output(self):
        result=self.run_source('hello')
        output=self.root/'out'
        export(result,output)
        original=(output/'chunks.jsonl').read_bytes()
        import os
        real_rename=os.rename
        calls=[]
        def fail_stage(source,destination):
            calls.append(str(source))
            if Path(source).name.startswith('.urc-stage-'):
                raise OSError('simulated publish error')
            return real_rename(source,destination)
        with patch('universal_rag_chunker.exporters.os.rename',side_effect=fail_stage):
            with self.assertRaises(OSError):
                export(result,output,overwrite=True)
        self.assertEqual((output/'chunks.jsonl').read_bytes(),original)
        self.assertFalse(list(self.root.glob('.urc-*')))

    def test_write_failure_leaves_no_output(self):
        result=self.run_source('hello')
        output=self.root/'out'
        with patch.object(Path,'write_bytes',side_effect=OSError('disk full')):
            with self.assertRaises(OSError):
                export(result,output)
        self.assertFalse(output.exists())
        self.assertFalse(list(self.root.glob('.urc-stage-*')))

    def test_overwrite_protects_unrelated_files(self):
        result=self.run_source('hello')
        output=self.root/'important'
        output.mkdir()
        note=output/'notes.txt'
        note.write_text('keep',encoding='utf-8')
        with self.assertRaisesRegex(OSError,'unrelated'):
            export(result,output,overwrite=True)
        self.assertEqual(note.read_text(encoding='utf-8'),'keep')

    def test_cli_exit_codes(self):
        source=self.root/'sample.txt'
        source.write_text('hello',encoding='utf-8')
        base=['chunk',str(source),'--output',str(self.root/'out')]
        self.assertEqual(self.cli(base),0)
        self.assertEqual(self.cli(base),5)
        self.assertEqual(self.cli(base+['--strategy','missing']),2)
        self.assertEqual(self.cli(['chunk',str(self.root/'missing.txt'),'--output',str(self.root/'other')]),3)
        source.write_text('',encoding='utf-8')
        self.assertEqual(self.cli(base),4)
        self.assertEqual(self.cli(['list-components']),0)


if __name__=='__main__':
    unittest.main()
