import os

class Config:
    # Text extraction parameters
    CHUNK_SIZE = 800  # Number of words per chunk. Increase -> more context but higher memory usage and less precise search
    MIN_CHUNK_SIZE = 3  # Minimum chunk size (in words)
    MAX_CHUNK_SIZE = 1500  # Maximum chunk size (in words)
    MAX_WORKERS_PDF = 4  # Number of PDFs processed in parallel. Increase if CPU is powerful, decrease if memory limited
    
    # Embedding parameters
    MODEL_NAME = 'all-MiniLM-L6-v2'  # Embedding model options:
                                     # - 'all-MiniLM-L6-v2': fast, lightweight, good tradeoff
                                     # - 'all-mpnet-base-v2': more accurate but slower
                                     # - 'multi-qa-MiniLM-L6-cos-v1': optimized for Q&A
    
    EMBEDDING_BATCH_SIZE = 32  # Number of texts processed together. Increase if GPU available,
                              # decrease if memory errors occur
    
    MAX_WORKERS_EMBEDDINGS = 4  # Embedding parallelization. Increase if GPU is powerful,
                               # decrease if using CPU or memory errors occur
    
    # Deduplication parameters
    DEDUP_THRESHOLD = 0.90  # Similarity threshold (0.0 to 1.0):
                           # - Closer to 1.0 -> stricter deduplication, keeps more texts
                           # - Closer to 0.0 -> aggressive deduplication, fewer duplicates
                           # - 0.90 is a good compromise, 0.95 to be conservative
    
    # Search parameters
    DEFAULT_TOP_K = 5  # Number of results displayed per search
                      # Increase for more results but may include less relevant matches
    
    MAX_DISPLAY_CHARS = 1500  # Length of excerpts in results
                             # Increase for more context, decrease for more concise view
    
    # Default file paths
    METADATA_PATH = "metadata.json"  # Temporary metadata file

    # General parameters
    VERBOSE = False # Enable/disable detailed messages, can slow down processing and should be used for debugging only
                    # True -> show all progress messages
                    # False -> show only progress bars and critical messages

    # Benchmark and estimation parameters
    BENCHMARK_FILE = "PDF_File_for_Benchmark.pdf"  # Reference file for benchmarking
    DEFAULT_PAGES_PER_SECOND = 100.0  # Default value if no benchmark
    DEFAULT_MB_PER_PAGE = 0.1       # Default value if no benchmark
    
    # Benchmark variables (updated by run_benchmark)
    pages_per_second = DEFAULT_PAGES_PER_SECOND
    mb_per_page = DEFAULT_MB_PER_PAGE

    # Database folder
    DATABASE_ROOT = os.path.join(":", "databases")  # Root folder to store all databases
    DATABASE_DEFAULT_NAME = "DB_default_name"  # Default database name

    # Exemple of section patterns
    section_patterns = [
        # Headers and structural elements
        r'(?i)Section \d+[\.\:].*?\n',     # Section headers
        r'(?i)Chapter \d+[\.\:].*?\n',     # Chapter headers
        r'(?i)Article \d+[\.\:].*?\n',     # Article headers
        r'(?i)Part \d+[\.\:].*?\n',        # Part headers
        r'(?i)Appendix [A-Z][\.\:].*?\n',  # Appendix headers

        # FR Headers and structural elements
        r'(?i)Chapitre \d+[\.\:].*?\n',    # Chapter headers
        r'(?i)Partie \d+[\.\:].*?\n',      # Part headers
        r'(?i)Annexe [A-Z][\.\:].*?\n',    # Appendix headers

        # Numbered and lettered sections
        r'\n\d+[\.\)] ',                   # Numbered paragraphs
        r'\n[A-Z][\.\)] ',                 # Letter-based sections
        r'\n[ivxIVX]+[\.\)] ',             # Roman numerals
        r'\n\d+\.\d+[\.\)] ',              # Subsections (1.1, 1.2, etc.)
        r'\n\d+\.\d+\.\d+[\.\)] ',         # Subsubsections (1.1.1, 1.1.2, etc.)

        # List markers
        r'\n[-•*▪◦○●] ',                   # Extended bullet points
        r'\n\d+\. ',                       # Numbered lists
        r'\n[a-z][\.\)] ',                 # Alphabetic lists
        r'\n[A-Z][\.\)] ',                 # Uppercase alphabetic lists

        # Whitespace and formatting
        r'\n\s*\n',                        # Multiple line breaks
        r'\t+',                            # Tabs
        r' {3,}',                          # Multiple spaces (3 or more)
        r'_{3,}',                          # Underline separators
        r'-{3,}',                          # Dash separators
        r'\*{3,}',                         # Asterisk separators
        r'={3,}',                          # Equal sign separators
        r'~{3,}',                          # Tilde separators
        r'\.{3,}',                         # Ellipsis
        r'…+',                             # Unicode ellipsis

        # Document structure elements
        r'(?i)Table of contents.*?\n',     # Table of contents
        r'(?i)Contents.*?\n',              # Alternative TOC
        r'(?i)Abstract.*?\n',              # Abstract
        r'(?i)Summary.*?\n',               # Summary
        r'(?i)Introduction.*?\n',          # Introduction
        r'(?i)Conclusion.*?\n',            # Conclusion
        r'(?i)Bibliography.*?\n',          # Bibliography
        r'(?i)References.*?\n',            # References
        r'(?i)Appendix.*?\n',              # Appendix
        r'(?i)Acknowledgments.*?\n',       # Acknowledgments

        # FR Document structure elements
        r'(?i)Table des matières.*?\n',    # Table of contents
        r'(?i)Sommaire.*?\n',              # Summary
        r'(?i)Résumé.*?\n',                # Abstract
        r'(?i)Introduction.*?\n',          # Introduction
        r'(?i)Bibliographie.*?\n',         # Bibliography
        r'(?i)Références.*?\n',            # References
        r'(?i)Annexe.*?\n',                # Appendix
        r'(?i)Remerciements.*?\n',         # Acknowledgments
        
        
        # Document sections
        r'(?i)Overview.*?\n',              # Overview sections
        r'(?i)Background.*?\n',            # Background sections
        r'(?i)Methods?.*?\n',              # Methods section
        r'(?i)Results?.*?\n',              # Results section
        r'(?i)Discussion.*?\n',            # Discussion section
        r'(?i)Materials?.*?\n',            # Materials section
    ]

