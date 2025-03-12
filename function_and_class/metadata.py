import json
from dataclasses import dataclass
from typing import List, Dict
from config import Config

@dataclass
class TextChunk:
    # Class representing a text passage and its metadata
    text: str           # Text content
    pdf_path: str       # Source PDF file path
    chunk_id: int       # Unique identifier for the chunk
    page_number: int    # Page number in PDF
    position_in_page: int # Position within the page

class MetadataManager:
    def __init__(self, save_path: str = Config.METADATA_PATH):
        # Initialize metadata manager with save path
        self.save_path = save_path
        self.metadata: Dict[str, List[TextChunk]] = {}

    def add_chunk(self, chunk: TextChunk) -> None:
        # Add a new chunk to metadata
        if chunk.pdf_path not in self.metadata:
            self.metadata[chunk.pdf_path] = []
        self.metadata[chunk.pdf_path].append(chunk)

    def save_metadata(self, save_path: str = None) -> None:
        # Save metadata to JSON file
        path_to_use = save_path or self.save_path
        serialized = {
            pdf_path: [chunk.__dict__ for chunk in chunks]
            for pdf_path, chunks in self.metadata.items()
        }
        with open(path_to_use, 'w', encoding='utf-8') as f:
            json.dump(serialized, f, ensure_ascii=False, indent=2)

    def load_metadata(self, load_path: str = None) -> None:
        # Load metadata from JSON file
        path_to_use = load_path or self.save_path
        try:
            with open(path_to_use, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.metadata = {
                    pdf_path: [TextChunk(**chunk) for chunk in chunks]
                    for pdf_path, chunks in data.items()
                }
        except FileNotFoundError:
            self.metadata = {}