"""Explicit component registration; no automatic third-party code loading."""
from .parsers import MarkdownParser, TextParser
from .office_parsers import PdfParser, DocxParser, XlsxParser
from .plugins import ExampleMetadataPlugin
from .strategies import FixedStrategy, RecursiveStrategy


class Registry:
    def __init__(self) -> None:
        self.parsers = {}
        self.strategies = {}
        self.plugins = {}
        for kind, components in (("parsers", [TextParser(), MarkdownParser(), PdfParser(), DocxParser(), XlsxParser()]),
                                 ("strategies", [FixedStrategy(), RecursiveStrategy()]),
                                 ("plugins", [ExampleMetadataPlugin()])):
            for component in components:
                self.register(kind, component)

    def register(self, kind, component) -> None:
        if kind not in ("parsers", "strategies", "plugins"):
            raise ValueError(f"Unknown component kind: {kind}")
        table = getattr(self, kind)
        if component.name in table:
            raise ValueError(f"Duplicate {kind} name: {component.name}")
        table[component.name] = component

    def resolve(self, kind, name):
        try:
            return getattr(self, kind)[name]
        except KeyError as error:
            raise ValueError(f"Unknown {kind} component: {name}") from error
