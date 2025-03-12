import os
import fitz  # PyMuPDF
import re
import concurrent.futures
import time
import psutil
from typing import List, Generator, Tuple
from tqdm import tqdm
from .metadata import MetadataManager, TextChunk
from .embeddings import EmbeddingManager
from .faiss_index import FAISSIndex
from config import Config


######################################################################
# Functions for extracting text from PDF files and processing them   #
######################################################################


def get_pdf_files(directory: str) -> List[str]:
    # Recursively get all PDF files in the given directory
    pdf_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.lower().endswith('.pdf'):
                pdf_files.append(os.path.join(root, file))
    return pdf_files

def clean_text(text: str) -> str:
    # Clean extracted PDF text
    # Note: Basic implementation - returns unmodified text
    return text

def extract_text_from_pdf(pdf_path: str) -> Generator[Tuple[str, int], None, None]:
    # Extract text from each PDF page
    try:
        doc = fitz.open(pdf_path)
        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text()
            cleaned_text = clean_text(text)
            if cleaned_text:
                yield cleaned_text, page_num + 1
    except Exception as e:
        print(f"Error extracting PDF {pdf_path}: {str(e)}")

def process_pdf(pdf_path: str) -> List[Tuple[str, int, str]]:
    # Process single PDF and return list of (text, page number, path) tuples
    results = []
    try:
        doc = fitz.open(pdf_path)
        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text()
            cleaned_text = clean_text(text)
            if cleaned_text:
                results.append((cleaned_text, page_num + 1, pdf_path))
    except Exception as e:
        print(f"Error processing PDF {pdf_path}: {str(e)}")
    return results

def parallel_extract_text_from_pdfs(pdf_files: List[str], max_workers: int = Config.MAX_WORKERS_PDF) -> List[Tuple[str, int, str]]:
    # Extract text from multiple PDFs in parallel
    all_results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(process_pdf, pdf_path): pdf_path for pdf_path in pdf_files}
        
        with tqdm(total=len(pdf_files), desc="Extracting PDFs") as pbar:
            for future in concurrent.futures.as_completed(futures):
                pdf_path = futures[future]
                try:
                    results = future.result()
                    all_results.extend(results)
                except Exception as e:
                    print(f"Error with {pdf_path}: {str(e)}")
                pbar.update(1)
                
    return all_results

def split_text_into_chunks(text: str) -> List[str]:
    # Split text into chunks based on natural units and size constraints
    # Compile patterns once for efficiency
    compiled_patterns = [re.compile(pattern) for pattern in Config.section_patterns]
    
    # Split into natural units using defined patterns
    chunks = [text]
    for pattern in compiled_patterns:
        new_chunks = []
        for chunk in chunks:
            # Split chunk using compiled pattern
            parts = pattern.split(chunk)
            # Filter out empty parts and join separators with next content
            for i in range(0, len(parts), 2):
                if i+1 < len(parts):
                    new_chunks.append(parts[i] + parts[i+1])
                elif parts[i]:
                    new_chunks.append(parts[i])
        chunks = new_chunks

    # Verify and adjust chunk sizes
    final_chunks = []
    current_chunk = []
    current_size = 0

    for chunk in chunks:
        words = chunk.split()
        chunk_size = len(words)

        if chunk_size > Config.MAX_CHUNK_SIZE:
            # Divide too large chunks into smaller ones
            while words:
                if current_size + Config.MAX_CHUNK_SIZE <= Config.MAX_CHUNK_SIZE:
                    current_chunk.extend(words[:Config.MAX_CHUNK_SIZE])
                    words = words[Config.MAX_CHUNK_SIZE:]
                    current_size = len(current_chunk)
                else:
                    final_chunks.append(' '.join(current_chunk))
                    current_chunk = []
                    current_size = 0
        else:
            if current_size + chunk_size > Config.MAX_CHUNK_SIZE:
                if current_chunk:
                    final_chunks.append(' '.join(current_chunk))
                current_chunk = words
                current_size = chunk_size
            else:
                current_chunk.extend(words)
                current_size += chunk_size

    # Add last chunk if any
    if current_chunk:
        final_chunks.append(' '.join(current_chunk))

    # Merge small chunks into larger ones
    merged_chunks = []
    current_chunk = []
    current_size = 0

    for chunk in final_chunks:
        words = chunk.split()
        chunk_size = len(words)

        if current_size + chunk_size <= Config.MAX_CHUNK_SIZE:
            current_chunk.extend(words)
            current_size += chunk_size
        else:
            if current_size >= Config.MIN_CHUNK_SIZE:
                merged_chunks.append(' '.join(current_chunk))
            current_chunk = words
            current_size = chunk_size

    if current_chunk and current_size >= Config.MIN_CHUNK_SIZE:
        merged_chunks.append(' '.join(current_chunk))

    return merged_chunks

#######################################
# PDFVectorDatabase class and methods #
#######################################

class PDFVectorDatabase:
    def __init__(self, input_directory: str):
        # Initialize database components
        self.input_directory = input_directory
        self.metadata_manager = MetadataManager()
        self.embedding_manager = EmbeddingManager()
        self.faiss_index = None

    def log(self, message: str) -> None:
        # Display message if verbose mode is enabled
        if Config.VERBOSE:
            print(message)

    def process_pdfs(self, progress_callback=None, skip_dedup: bool = True, db_name: str = Config.DATABASE_DEFAULT_NAME):
        # Create database directory
        database_path = os.path.join(Config.DATABASE_ROOT, db_name)
        os.makedirs(database_path, exist_ok=True)

        # Get and process all PDFs from input directory
        pdf_files = get_pdf_files(self.input_directory)
        
        self.log("\nExtracting text from PDFs...")
        extracted_texts = parallel_extract_text_from_pdfs(pdf_files)
        
        # Process extracted texts into chunks
        all_chunks = []
        chunk_id = 0
        total_chunks = 0
        total_pages = 0
        
        for text, page_num, pdf_path in extracted_texts:
            chunks = split_text_into_chunks(text)
            total_pages += 1
            
            for pos, chunk in enumerate(chunks):
                text_chunk = TextChunk(
                    text=chunk,
                    pdf_path=pdf_path,
                    chunk_id=chunk_id,
                    page_number=page_num,
                    position_in_page=pos
                )
                all_chunks.append(text_chunk)
                self.metadata_manager.add_chunk(text_chunk)
                chunk_id += 1
                total_chunks += 1
                
            if progress_callback and Config.VERBOSE:
                progress_callback(pdf_path, len(chunks), 1)

        # Generate embeddings
        self.log("\nGenerating embeddings in parallel...")
        texts = [chunk.text for chunk in all_chunks]
        embeddings = self.embedding_manager.generate_embeddings(texts)
        
        # Handle deduplication
        if skip_dedup:
            self.log("Skipping deduplication...")
            unique_embeddings = embeddings
            unique_indices = list(range(len(embeddings)))
        else:
            self.log("Deduplicating vectors...")
            unique_embeddings, unique_indices = self.embedding_manager.deduplicate_vectors(embeddings)
            self.log(f"Unique vectors: {len(unique_embeddings)} out of {len(embeddings)} total")

        # Create and save FAISS index
        self.log("Creating FAISS index...")
        self.faiss_index = FAISSIndex(unique_embeddings.shape[1])
        self.faiss_index.add_vectors(unique_embeddings)
        
        # Save database files
        self.log("Saving database files...")
        self.metadata_manager.save_metadata(os.path.join(database_path, f"{db_name}.json"))
        self.faiss_index.save_index(os.path.join(database_path, f"{db_name}.faiss"))

    def search(self, query: str, k: int = Config.DEFAULT_TOP_K) -> List[dict]:
        # Search the vector database for similar texts
        query_embedding = self.embedding_manager.generate_embeddings([query])
        distances, indices = self.faiss_index.search(query_embedding, k)
        
        # Format search results
        results = []
        all_chunks = []
        for chunks in self.metadata_manager.metadata.values():
            all_chunks.extend(chunks)
        
        for i, (distance, idx) in enumerate(zip(distances[0], indices[0])):
            if idx < len(all_chunks):
                chunk = all_chunks[idx]
                results.append({
                    'text': chunk.text,
                    'pdf_path': chunk.pdf_path,
                    'page': chunk.page_number,
                    'similarity_score': 1 - (distance / 2)
                })
        
        return results

    def load_existing_database(self, db_name: str = ""):
        # Load an existing vector database
        print("\nLoading existing database...")
        try:
            db_path = os.path.join(Config.DATABASE_ROOT, db_name)
            # Load metadata
            self.metadata_manager.load_metadata(os.path.join(db_path, f"{db_name}.json"))
            
            # Load FAISS index
            embeddings_dim = self.embedding_manager.model.get_sentence_embedding_dimension()
            self.faiss_index = FAISSIndex(embeddings_dim)
            self.faiss_index.load_index(os.path.join(db_path, f"{db_name}.faiss"))
            
            print("Database loaded successfully!")
            return True
        except Exception as e:
            print(f"Error loading database: {str(e)}")
            return False

    def deduplicate_existing_database(self):
        # Deduplicate the loaded database
        print("\nDeduplicating loaded database...")
        try:
            embeddings = []
            all_chunks = []
            for chunks in self.metadata_manager.metadata.values():
                all_chunks.extend(chunks)
                embeddings.extend(self.embedding_manager.generate_embeddings([chunk.text for chunk in chunks]))
            
            unique_embeddings, unique_indices = self.embedding_manager.deduplicate_vectors(embeddings)
            self.log(f"Vector deduplication: {len(unique_embeddings)} unique vectors out of {len(embeddings)} total")
            
            # Update metadata
            new_metadata = {pdf_path: [all_chunks[i] for i in unique_indices] 
                            for pdf_path, chunks in self.metadata_manager.metadata.items()}
            self.metadata_manager.metadata = new_metadata
            
            # Update FAISS index
            self.faiss_index = FAISSIndex(unique_embeddings.shape[1])
            self.faiss_index.add_vectors(unique_embeddings)
            print("Deduplication completed successfully!")
        except Exception as e:
            print(f"Error during deduplication: {str(e)}")

    def display_all_chunks(self) -> None:
        # Display all chunks in the loaded database
        print("\n === Displaying all chunks ===")
        
        if not self.metadata_manager.metadata:
            print("Metadata is empty or not loaded!")
            return
        
        total_chunks = 0
        total_pdfs = len(self.metadata_manager.metadata)
        
        for pdf_path, chunks in self.metadata_manager.metadata.items():
            print(f"\nFile: {os.path.basename(pdf_path)}")
            print("-" * 50)
            
            for chunk in chunks:
                total_chunks += 1
                print(f"\nChunk ID: {chunk.chunk_id}")
                print(f"Page: {chunk.page_number}")
                print(f"Position: {chunk.position_in_page}")
                print(f"Texte:\n{chunk.text}\n")
                print("-" * 30)
        
        print("\n=== Statistiques ===")
        print(f"Number of PDFs: {total_pdfs}")
        print(f"Number of chunks: {total_chunks}")
        print("=" * 50)

def create_new_database():
    # Create a new vector database
    db_name = input("Enter new database name: ")
    input_directory = input("Enter directory with PDF files you want to process: ")
    
    db = PDFVectorDatabase(input_directory)
    pdf_files = get_pdf_files(db.input_directory)

    if not pdf_files:
        print("No PDF files found in the input directory!")
        return None

    # Estimation du temps et de la mémoire
    est_minutes, est_memory = estimate_processing_time(pdf_files)
    
    print("\n=== Estimations ===")
    print(f"Number of PDF files: {len(pdf_files)}")
    print(f"Estimated processing time: {est_minutes:.1f} minutes")
    print(f"Estimated memory usage: {est_memory:.1f} GB")
    
    confirmation = input("\nDo you want to proceed with processing? (Y/n): ").lower() == 'y'
    if confirmation:
        print("Cancelled processing.")
        return None

    # Initialise counters
    total_chunks = 0
    total_pages = 0

    # Ask user if they want to skip deduplication
    skip_dedup = input("\nDo you want to skip deduplication? (y/N): ").lower() == 'y'
    if skip_dedup:
        print("Skipping deduplication step...")
    else :
        skip_dedup = False

    # Show PDF files to be processed if verbose
    if Config.VERBOSE:
        print("\n=== Fichiers PDF à traiter ===")
        for i, pdf in enumerate(pdf_files, 1):
            print(f"{i}. {pdf}")

    def progress_callback(pdf_path, chunks, pages):
        nonlocal total_chunks, total_pages
        total_chunks += chunks
        total_pages += pages
        if Config.VERBOSE:
            print(f"\nProcessing {os.path.basename(pdf_path)}")
            print(f"Processed pages: {pages}")
            print(f"Extracted chunks: {chunks}")
            print(f"Total chunks: {total_chunks}")
            print(f"Total pages: {total_pages}")

    db.process_pdfs(progress_callback if Config.VERBOSE else None, skip_dedup, db_name)
    return db

def load_existing_database():
    # Load an existing vector database
    print("\nDisplaying existing databases...")
    try:
        # List directories only
        databases = [d for d in os.listdir(Config.DATABASE_ROOT) 
                    if os.path.isdir(os.path.join(Config.DATABASE_ROOT, d))]
        
        for i, db in enumerate(databases, 1):
            print(f"{i}. {db}")
        
        if not databases:
            print("No databases found!")
            return None
        
        # Ask user to select a database
        db_name = input("\nEnter database name to load: ")
        
        # Initialize and load database
        db = PDFVectorDatabase("")  # Empty input directory as we're loading existing db
        if db.load_existing_database(db_name):
            return db
    except Exception as e:
        print(f"Error loading database: {str(e)}")
    
    return None

####################################################
# Benchmarking and estimation functions for Config #
####################################################

def estimate_processing_time(pdf_files: List[str]) -> tuple[float, float]:
    # Estimate processing time and memory usage for PDF files
    total_pages = 0
    try:
        # Count total pages in all PDF files
        for pdf_path in pdf_files:
            doc = fitz.open(pdf_path)
            total_pages += len(doc)
            doc.close()
            
        # Calculate estimated time and memory usages
        estimated_minutes = (total_pages / Config.pages_per_second) / 60
        estimated_memory_gb = (total_pages * Config.mb_per_page) / 1024
        
        return estimated_minutes, estimated_memory_gb
        
    except Exception as e:
        print(f"Error estimating processing time: {str(e)}")
        return 0, 0

def run_benchmark() -> tuple[float, float]:
    # Run a benchmark to estimate processing speed and memory usage
    benchmark_path = Config.BENCHMARK_FILE
    if not os.path.exists(benchmark_path):
        print(f"Benchmark file not found: {benchmark_path}")
        return Config.DEFAULT_PAGES_PER_SECOND, Config.DEFAULT_MB_PER_PAGE

    try:
        print("\nStarting benchmark...")
        # Initialize time and memory tracking
        start_time = time.time()
        start_memory = psutil.Process().memory_info().rss / (1024 * 1024)  # MB

        # Open benchmark PDF and count pages
        doc = fitz.open(benchmark_path)
        num_pages = len(doc)
        
        # Simulate text extraction and chunking
        all_chunks = []
        with tqdm(total=num_pages, desc="Simulate pages processing", unit="pages") as pbar:
            for page_num in range(num_pages):
                page = doc[page_num]
                text = page.get_text()
                cleaned_text = clean_text(text)
                if cleaned_text:
                    chunks = split_text_into_chunks(cleaned_text)
                    all_chunks.extend(chunks)
                pbar.update(1)

        # Simulate embeddings generation
        total_chars = 0
        with tqdm(total=len(all_chunks), desc="Simulate embeddings", unit="chunks") as pbar:
            for chunk in all_chunks:
                total_chars += len(chunk)
                pbar.update(1)
        
        # Simulate memory usage for embeddings
        simulated_embedding_size = total_chars * 4  

        end_time = time.time()
        end_memory = psutil.Process().memory_info().rss / (1024 * 1024)  # MB
        
        # Add simulated memory usage
        end_memory += simulated_embedding_size / (1024 * 1024)  # MB

        # Calcul of the benchmark results
        processing_time = end_time - start_time
        pages_per_second = num_pages / processing_time
        mb_per_page = (end_memory - start_memory) / num_pages

        # Update Config values
        Config.pages_per_second = pages_per_second
        Config.mb_per_page = mb_per_page

        # Display benchmark results
        print("\n=== Benchmark Results ===")
        print(f"Processed pages: {num_pages}")
        print(f"Generated chunks: {len(all_chunks)}")
        print(f"Text volume: {total_chars:,} characters")
        print(f"Total time: {processing_time:.2f} seconds")
        print(f"Speed: {pages_per_second:.2f} pages/second")
        print(f"Memory per page: {mb_per_page:.2f} MB")

        doc.close()
        return pages_per_second, mb_per_page

    except Exception as e:
        print(f"Error running benchmark: {str(e)}")
        return Config.DEFAULT_PAGES_PER_SECOND, Config.DEFAULT_MB_PER_PAGE
