import json
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / 'src/universal_rag_chunker/schemas'
ROOT.mkdir(parents=True, exist_ok=True)

def obj(properties, required=None):
    return {'type':'object', 'properties':properties, 'required':list(properties) if required is None else required, 'additionalProperties':False}

def arr(item, minimum=0):
    return {'type':'array','items':item,'minItems':minimum}

s = {'type':'string'}
n = {'type':'integer','minimum':0}
version = {'const':'1.0','type':'string'}
hexhash = {'type':'string','pattern':'^[0-9a-f]{64}$'}
def identity(prefix):
    return {'type':'string','pattern':'^'+prefix+'_[0-9a-f]{64}$'}
component = obj({'name':s,'version':s})
block = obj({'block_id':identity('block'), 'type':{'enum':['heading','paragraph','list_item','code'],'type':'string'},
    'order':n,'parent_id':{'type':['string','null']},'text':s,
    'locator':obj({'kind':{'const':'text','type':'string'},'start':n,'end':n}), 'attributes':{'type':'object'}})
document = obj({'schema_version':version,'document_id':identity('doc'),
    'source':obj({'source_id':{'type':'string','minLength':1},'display_name':s,'media_type':s,'content_sha256':hexhash}),
    'parser':obj({'name':s,'version':s,'config_digest':hexhash}), 'document_type':s, 'blocks':arr(block,1), 'metadata':{'type':'object'}})
chunk = obj({'schema_version':version,'chunk_id':identity('chunk'),'document_id':identity('doc'),'order':n,
    'text':{'type':'string','minLength':1},'kind':{'type':'string','enum':['text','code']},
    'heading_path':arr(obj({'block_id':identity('block'),'title':s})),
    'source_spans':arr(obj({'block_id':identity('block'),'start':n,'end':n,'role':{'type':'string','const':'body'}}),1),
    'size':obj({'characters':n}),
    'provenance':obj({'strategy':component,'plugins':arr(component),'pipeline_version':s,'config_digest':hexhash}),
    'metadata':{'type':'object'}})
for name, schema in [('document-ir',document),('chunk',chunk)]:
    schema['$schema'] = 'https://json-schema.org/draft/2020-12/schema'
    schema['title'] = name + ' 1.0'
    (ROOT / (name+'-1.0.schema.json')).write_text(json.dumps(schema,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

# Keep 1.0 unchanged for previously exported runs. 1.1 adds binary locators.
document_new = deepcopy(document)
chunk_new = deepcopy(chunk)
for schema in (document_new, chunk_new):
    schema['properties']['schema_version'] = {'type':'string','const':'1.1'}
    schema['title'] = schema['title'].replace('1.0','1.1')
source_schema = document_new['properties']['source']
source_schema['properties']['extracted_text_sha256'] = hexhash
new_block = document_new['properties']['blocks']['items']
new_block['properties']['type']['enum'].append('table_row')
positive = {'type':'integer','minimum':1}
new_block['properties']['locator'] = {'oneOf': [
    deepcopy(block['properties']['locator']),
    obj({'kind':{'type':'string','const':'page'},'page':positive}),
    obj({'kind':{'type':'string','const':'docx'},'body_index':positive,'row':positive}, ['kind','body_index']),
    obj({'kind':{'type':'string','const':'sheet'},'sheet_name':{'type':'string','minLength':1},
         'row':positive,'column_start':positive,'column_end':positive})
]}
chunk_new['properties']['kind']['enum'].append('table')
for name, schema in [('document-ir',document_new),('chunk',chunk_new)]:
    (ROOT / (name+'-1.1.schema.json')).write_text(json.dumps(schema,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
