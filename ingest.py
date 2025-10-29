#!/usr/bin/env python3
"""
Collegemate Ingest Script
Takes text input (manual or from file) and stores embeddings into ChromaDB collection
"""

import os
import sys
import argparse
import uuid
from datetime import datetime
from dotenv import load_dotenv
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

# Load environment variables
load_dotenv()

def initialize_chromadb():
    """Initialize ChromaDB client and collection"""
    chroma_client = chromadb.Client(Settings(
        chroma_db_impl="duckdb+parquet",
        persist_directory="./chroma_db"
    ))
    
    try:
        collection = chroma_client.get_collection("collegemate_knowledge")
    except:
        collection = chroma_client.create_collection("collegemate_knowledge")
    
    return collection

def ingest_text(text, metadata=None, collection=None):
    """Ingest text into ChromaDB collection"""
    if collection is None:
        collection = initialize_chromadb()
    
    if metadata is None:
        metadata = {}
    
    # Generate unique ID for the document
    doc_id = str(uuid.uuid4())
    
    # Add timestamp to metadata
    metadata['timestamp'] = datetime.now().isoformat()
    metadata['source'] = metadata.get('source', 'cli')
    
    # Store in ChromaDB
    collection.add(
        documents=[text],
        metadatas=[metadata],
        ids=[doc_id]
    )
    
    print(f"✅ Successfully ingested text with ID: {doc_id}")
    return doc_id

def ingest_file(file_path, metadata=None):
    """Ingest text from a file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            text = file.read()
        
        if metadata is None:
            metadata = {}
        metadata['source'] = 'file'
        metadata['file_path'] = file_path
        
        return ingest_text(text, metadata)
    except FileNotFoundError:
        print(f"❌ Error: File '{file_path}' not found")
        return None
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return None

def interactive_mode():
    """Interactive mode for manual text input"""
    print("📝 Interactive Text Ingestion Mode")
    print("Enter your text (type 'END' on a new line to finish):")
    print("-" * 50)
    
    lines = []
    while True:
        line = input()
        if line.strip() == 'END':
            break
        lines.append(line)
    
    text = '\n'.join(lines)
    
    if text.strip():
        metadata = {'source': 'interactive'}
        ingest_text(text, metadata)
    else:
        print("❌ No text provided")

def main():
    parser = argparse.ArgumentParser(description='Collegemate Text Ingestion Tool')
    parser.add_argument('--file', '-f', help='Path to text file to ingest')
    parser.add_argument('--text', '-t', help='Text to ingest directly')
    parser.add_argument('--interactive', '-i', action='store_true', 
                       help='Interactive mode for manual input')
    parser.add_argument('--metadata', '-m', help='JSON metadata string')
    
    args = parser.parse_args()
    
    # Parse metadata if provided
    metadata = None
    if args.metadata:
        try:
            import json
            metadata = json.loads(args.metadata)
        except json.JSONDecodeError:
            print("❌ Error: Invalid JSON metadata")
            return
    
    # Determine mode
    if args.file:
        ingest_file(args.file, metadata)
    elif args.text:
        ingest_text(args.text, metadata)
    elif args.interactive:
        interactive_mode()
    else:
        # Default to interactive mode
        interactive_mode()

if __name__ == "__main__":
    main()
