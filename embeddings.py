import numpy as np
import concurrent.futures
from typing import List, Tuple, Dict
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
from tqdm import tqdm
from config import Config

class EmbeddingManager:
    def __init__(self, 
                 model_name: str = Config.MODEL_NAME, 
                 batch_size: int = Config.EMBEDDING_BATCH_SIZE):
        #Initialize the embedding manager with a model and batch size
        self.model = SentenceTransformer(model_name)
        self.embeddings: Dict[str, np.ndarray] = {}
        self.batch_size = batch_size

    def generate_embeddings_batch(self, text_chunks: List[str]) -> np.ndarray:
        #Generate embeddings for a batch of text chunks
        return self.model.encode(text_chunks, show_progress_bar=False)

    def generate_embeddings(self, 
                          text_chunks: List[str], 
                          max_workers: int = Config.MAX_WORKERS_EMBEDDINGS) -> np.ndarray:
        
        # Split chunks into batches
        batches = [text_chunks[i:i + self.batch_size] 
                  for i in range(0, len(text_chunks), self.batch_size)]
        
        all_embeddings = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(self.generate_embeddings_batch, batch): i 
                      for i, batch in enumerate(batches)}
            
            with tqdm(total=len(batches), desc="Generating embeddings") as pbar:
                for future in concurrent.futures.as_completed(futures):
                    batch_idx = futures[future]
                    try:
                        embeddings = future.result()
                        all_embeddings.append((batch_idx, embeddings))
                    except Exception as e:
                        print(f"Error processing batch {batch_idx}: {str(e)}")
                    pbar.update(1)
        
        # Reorder results to match original sequence
        all_embeddings.sort(key=lambda x: x[0])
        return np.vstack([emb for _, emb in all_embeddings])

    def deduplicate_vectors(self, 
                          new_embeddings: np.ndarray, 
                          threshold: float = Config.DEDUP_THRESHOLD) -> Tuple[np.ndarray, List[int]]:
        #Deduplicate vectors based on cosine similarity
        if len(new_embeddings) == 0:
            return np.array([]), []

        # Initialize with first vector
        unique_embeddings = [new_embeddings[0]]
        unique_indices = [0]

        # Process remaining vectors
        with tqdm(total=len(new_embeddings)-1, 
                 desc="Deduplicating vectors", 
                 unit="vectors") as pbar:
            for i in range(1, len(new_embeddings)):
                current_vector = new_embeddings[i].reshape(1, -1)
                similarities = cosine_similarity(
                    current_vector, 
                    np.array(unique_embeddings)
                )
                
                # Keep vector if no similar vectors found
                if not any(sim > threshold for sim in similarities[0]):
                    unique_embeddings.append(new_embeddings[i])
                    unique_indices.append(i)
                
                pbar.update(1)

        return np.array(unique_embeddings), unique_indices