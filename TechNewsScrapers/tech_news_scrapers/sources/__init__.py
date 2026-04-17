from .apple_ml import scrape_apple_ml
from .deepmind import scrape_deepmind
from .huggingface import scrape_huggingface
from .import_ai import scrape_import_ai
from .paperswithcode import scrape_paperswithcode
from .the_batch import scrape_the_batch
from .the_neuron import scrape_the_neuron
from .the_rundown_ai import scrape_the_rundown_ai
from .tldr_ai import scrape_tldr_ai

__all__ = [
    "scrape_huggingface",
    "scrape_deepmind",
    "scrape_apple_ml",
    "scrape_paperswithcode",
    "scrape_the_batch",
    "scrape_tldr_ai",
    "scrape_the_neuron",
    "scrape_the_rundown_ai",
    "scrape_import_ai",
]

