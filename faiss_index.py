import faiss
import numpy as np
from typing import Tuple

class FAISSIndex:
    def __init__(self, dimension: int):
        # Initialize FAISS index with specified dimension
        self.dimension = dimension
        self.index = faiss.IndexFlatL2(dimension)

    def add_vectors(self, vectors: np.ndarray) -> None:
        # Add vectors to FAISS index if not empty
        # Converts to float32 for compatibility
        if len(vectors) > 0:
            self.index.add(vectors.astype('float32'))

    def save_index(self, path: str) -> None:
        # Save FAISS index to disk at specified path
        faiss.write_index(self.index, path)

    def load_index(self, path: str) -> None:
        # Load FAISS index from disk
        self.index = faiss.read_index(path)

    def search(self, 
              query_vector: np.ndarray, 
              k: int = 5) -> Tuple[np.ndarray, np.ndarray]:
        # Search for k nearest neighbors in the index
        # Args:
        #     query_vector: Vector to search for
        #     k: Number of nearest neighbors to return
        # Returns:
        #     Tuple of (distances, indices) arrays
        return self.index.search(query_vector.astype('float32'), k)