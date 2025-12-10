"""
Integration pipeline

API Spec load -> Document conversion -> Embedding -> Vector Store
"""

from .spec_indexer import SpecIndexer

__all__ = [
    "SpecIndexer",
]
