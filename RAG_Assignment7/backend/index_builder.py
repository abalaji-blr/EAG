#!/usr/bin/env python3
"""
Index Builder for Chrome Semantic Search Extension
-------------------------------------------------
This script builds a FAISS index from collected web pages.
It can be run in Google Colab to generate an index file
that can be downloaded and used with the Chrome extension.
"""

import os
import json
import time
import argparse
import numpy as np
import pandas as pd
from pathlib import Path
from tqdm import tqdm
import faiss

# For running in Colab, make sure to install requirements
try:
    import nomic
except ImportError:
    print("Installing requirements...")
    # Uncomment these lines to run in Colab
    # !pip install nomic-embed torch faiss-cpu tqdm

# Import our modules
from perception import PerceptionModule
from memory import MemoryModule, PageChunk
from decision import DecisionModule
from action import ActionModule
from agent import EmbeddingModule


class IndexBuilder:
    """Builds a FAISS index from web pages."""
    
    def __init__(self, data_dir="data", output_dir="index"):
        # Set up directories
        self.data_dir = Path(data_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize modules
        self.perception = PerceptionModule()
        self.memory = MemoryModule(index_dir=output_dir)
        self.decision = DecisionModule()
        self.embedding = EmbeddingModule()
    
    def process_html_files(self, batch_size=10):
        """Process HTML files in the data directory."""
        # Find all HTML files
        html_files = list(self.data_dir.glob("*.html"))
        if not html_files:
            print(f"No HTML files found in {self.data_dir}")
            return
        
        print(f"Found {len(html_files)} HTML files to process")
        
        # Process files in batches
        for i in range(0, len(html_files), batch_size):
            batch = html_files[i:i+batch_size]
            self._process_batch(batch)
            
            # Save after each batch
            self.memory.save_index()
            print(f"Processed {min(i+batch_size, len(html_files))}/{len(html_files)} files")
    
    def _process_batch(self, html_files):
        """Process a batch of HTML files."""
        all_chunks = []
        all_texts = []
        
        # Process each file
        for html_file in tqdm(html_files):
            try:
                # Extract URL from filename
                url = self._extract_url_from_filename(html_file.name)
                
                # Read HTML content
                with open(html_file, 'r', encoding='utf-8', errors='ignore') as f:
                    html_content = f.read()
                
                # Extract content
                page_content = self.perception.extract_content(url, html_content)
                
                # Skip if no content
                if not page_content.text.strip():
                    continue
                
                # Prepare content for chunking
                full_text = f"{page_content.title}\n\n"
                if page_content.headings:
                    full_text += "Headings: " + " | ".join(page_content.headings) + "\n\n"
                full_text += page_content.text
                
                # Split into chunks
                chunks_text = self.decision.chunk_text(full_text)
                
                # Create page chunks
                for chunk_text in chunks_text:
                    chunk = PageChunk(
                        url=url,
                        text=chunk_text,
                        title=page_content.title,
                        chunk_type="content",
                        timestamp=time.time()
                    )
                    all_chunks.append(chunk)
                    all_texts.append(chunk_text)
                    
            except Exception as e:
                print(f"Error processing {html_file}: {e}")
        
        # Generate embeddings for all chunks
        if all_texts:
            print(f"Generating embeddings for {len(all_texts)} chunks")
            embeddings = self.embedding.generate_embeddings(all_texts)
            
            # Add to index
            self.memory.add_embeddings(all_chunks, embeddings)
    
    def _extract_url_from_filename(self, filename):
        """Extract URL from filename."""
        # Simple implementation - in practice, you'd use a more robust method
        name = filename.replace('.html', '')
        return f"http://{name}"  # Placeholder URL
    
    def process_jsonl_data(self, jsonl_file):
        """Process data from a JSONL file with URLs and content."""
        if not os.path.exists(jsonl_file):
            print(f"File not found: {jsonl_file}")
            return
        
        # Read JSONL data
        pages = []
        with open(jsonl_file, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    data = json.loads(line.strip())
                    pages.append(data)
                except json.JSONDecodeError:
                    continue
        
        print(f"Found {len(pages)} pages in {jsonl_file}")
        
        # Process pages in batches
        batch_size = 10
        for i in range(0, len(pages), batch_size):
            batch = pages[i:i+batch_size]
            self._process_jsonl_batch(batch)
            
            # Save after each batch
            self.memory.save_index()
            print(f"Processed {min(i+batch_size, len(pages))}/{len(pages)} pages")
    
    def _process_jsonl_batch(self, pages):
        """Process a batch of pages from JSONL data."""
        all_chunks = []
        all_texts = []
        
        for page in tqdm(pages):
            try:
                url = page.get('url', '')
                html_content = page.get('content', '')
                
                if not url or not html_content:
                    continue
                
                # Extract content
                page_content = self.perception.extract_content(url, html_content)
                
                # Skip if no content
                if not page_content.text.strip():
                    continue
                
                # Prepare content for chunking
                full_text = f"{page_content.title}\n\n"
                if page_content.headings:
                    full_text += "Headings: " + " | ".join(page_content.headings) + "\n\n"
                full_text += page_content.text
                
                # Split into chunks
                chunks_text = self.decision.chunk_text(full_text)
                
                # Create page chunks
                for chunk_text in chunks_text:
                    chunk = PageChunk(
                        url=url,
                        text=chunk_text,
                        title=page_content.title,
                        chunk_type="content",
                        timestamp=time.time()
                    )
                    all_chunks.append(chunk)
                    all_texts.append(chunk_text)
                    
            except Exception as e:
                print(f"Error processing page {page.get('url')}: {e}")
        
        # Generate embeddings for all chunks
        if all_texts:
            print(f"Generating embeddings for {len(all_texts)} chunks")
            embeddings = self.embedding.generate_embeddings(all_texts)
            
            # Add to index
            self.memory.add_embeddings(all_chunks, embeddings)
    
    def get_index_stats(self):
        """Get statistics about the index."""
        return self.memory.get_stats()


def main():
    parser = argparse.ArgumentParser(description='Build FAISS index for Chrome Semantic Search')
    parser.add_argument('--data-dir', default='data', help='Directory containing HTML files')
    parser.add_argument('--output-dir', default='index', help='Output directory for index files')
    parser.add_argument('--jsonl-file', help='JSONL file with URLs and content')
    
    args = parser.parse_args()
    
    builder = IndexBuilder(data_dir=args.data_dir, output_dir=args.output_dir)
    
    if args.jsonl_file:
        builder.process_jsonl_data(args.jsonl_file)
    else:
        builder.process_html_files()
    
    stats = builder.get_index_stats()
    print("\nIndex statistics:")
    for key, value in stats.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()
