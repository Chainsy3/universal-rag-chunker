"""Universal RAG Chunker: no file writes until export is requested."""
from .config import Config
from .pipeline import Pipeline
from .registry import Registry

__version__ = "0.2.0"
__all__ = ["Config", "Pipeline", "Registry"]
