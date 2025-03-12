# PDF to vectorial DB
A Python-based tool for creating searchable vector databases from PDF documents. Uses neural embeddings to enable semantic search capabilities across your PDF collections.

## 🚀 Features

- **Recursive PDF Processing**: Automatically processes all PDFs in a directory and its subdirectories
- **Semantic Search**: Uses neural embeddings to find semantically similar content
- **Configurable Settings**: Easy customization via configuration file
- **Deduplication**: Optional content deduplication to remove similar text chunks
- **Multi-language Support**: Works with any language supported by the embedding model

## 📋 Requirements

- Python 3.10+
- PyMuPDF (fitz) == 1.23.8
- faiss-cpu == 1.7.4
- sentence-transformers == 2.5.1
- scikit-learn == 1.4.0
- numpy >= 1.24.0
- tqdm >= 4.66.1
- psutil >= 5.9.0
- typing-extensions >= 4.9.0
- dataclasses >= 0.6

## 🛠️ Installation

```bash
git clone https://github.com/Cl0s3WitZ/pdf-to-vectordb.git
cd pdf-to-vectordb
pip install -r requirements.txt
```

## 🔧 Configuration

Edit `config.py` to customize:
- Chunk sizes
- Model selection
- Display parameters
- Database storage locations
- Regular expressions for text sections

## 📖 Usage

Run the main script:
```bash
python main.py
```
