import faiss
import numpy as np
import pickle
import os
import argparse

def inspect_faiss_index(index_path, output_dir=None):
    """
    Load and inspect a FAISS index, extracting vectors and metadata if available.
    
    Args:
        index_path: Path to the .faiss index file
        output_dir: Directory to save output files (optional)
    """
    print(f"Loading FAISS index from {index_path}...")
    index = faiss.read_index(index_path)
    
    # Get basic information about the index
    print("\n=== FAISS Index Information ===")
    print(f"Index type: {type(index).__name__}")
    print(f"Dimension: {index.d}")
    print(f"Number of vectors: {index.ntotal}")
    
    # Try to determine if it's a flat index or other type
    index_type = type(index).__name__
    
    # Check if the index is trained
    if hasattr(index, 'is_trained'):
        print(f"Is trained: {index.is_trained}")
    
    # Extract vectors if possible
    vectors = None
    if isinstance(index, faiss.IndexFlat) or hasattr(index, 'reconstruct'):
        print("\nExtracting vectors...")
        vectors = np.zeros((index.ntotal, index.d), dtype=np.float32)
        for i in range(index.ntotal):
            vectors[i] = index.reconstruct(i)
        print(f"Successfully extracted {len(vectors)} vectors of dimension {index.d}")
        
        # Calculate some basic statistics about the vectors
        if len(vectors) > 0:
            print("\n=== Vector Statistics ===")
            print(f"Mean: {np.mean(vectors, axis=0)[:5]}... (truncated)")
            print(f"Std: {np.std(vectors, axis=0)[:5]}... (truncated)")
            print(f"Min: {np.min(vectors, axis=0)[:5]}... (truncated)")
            print(f"Max: {np.max(vectors, axis=0)[:5]}... (truncated)")
    else:
        print("\nCannot directly extract vectors from this index type.")
    
    # Look for index_metadata.pickle file in the same directory
    metadata = None
    metadata_path = os.path.join(os.path.dirname(index_path), "index_metadata.pickle")
    if os.path.exists(metadata_path):
        try:
            print(f"\nLoading metadata from {metadata_path}...")
            with open(metadata_path, "rb") as f:
                metadata = pickle.load(f)
            print(f"Metadata keys: {list(metadata.keys())}")
        except Exception as e:
            print(f"Error loading metadata: {e}")
    else:
        print("\nNo metadata file found.")
    
    # Try to find id_to_text.pickle or similar files
    id_mapping = None
    possible_mapping_files = [
        os.path.join(os.path.dirname(index_path), "id_to_text.pickle"),
        os.path.join(os.path.dirname(index_path), "id_to_docid.pickle"),
        os.path.join(os.path.dirname(index_path), "id_mapping.pickle")
    ]
    
    for mapping_file in possible_mapping_files:
        if os.path.exists(mapping_file):
            try:
                print(f"\nLoading ID mapping from {mapping_file}...")
                with open(mapping_file, "rb") as f:
                    id_mapping = pickle.load(f)
                print(f"Found mapping for {len(id_mapping)} IDs")
                # Show sample of the mapping
                sample_keys = list(id_mapping.keys())[:3]
                print(f"Sample mappings: {sample_keys} → {[id_mapping[k] for k in sample_keys]}")
                break
            except Exception as e:
                print(f"Error loading ID mapping: {e}")
    
    # Save to output files if requested
    if output_dir and vectors is not None:
        os.makedirs(output_dir, exist_ok=True)
        
        # Save vectors to .npy file
        vector_file = os.path.join(output_dir, "vectors.npy")
        print(f"\nSaving vectors to {vector_file}...")
        np.save(vector_file, vectors)
        
        # Save metadata to .pickle if available
        if metadata:
            metadata_file = os.path.join(output_dir, "metadata.pickle")
            print(f"Saving metadata to {metadata_file}...")
            with open(metadata_file, "wb") as f:
                pickle.dump(metadata, f)
        
        # Save ID mapping to .pickle if available
        if id_mapping:
            mapping_file = os.path.join(output_dir, "id_mapping.pickle")
            print(f"Saving ID mapping to {mapping_file}...")
            with open(mapping_file, "wb") as f:
                pickle.dump(id_mapping, f)
                
        # Create a sample CSV with vectors and metadata (if available)
        sample_size = min(100, index.ntotal)
        if sample_size > 0:
            import csv
            sample_file = os.path.join(output_dir, "sample.csv")
            print(f"Saving sample of {sample_size} entries to {sample_file}...")
            
            with open(sample_file, 'w', newline='') as f:
                writer = csv.writer(f)
                
                # Create header row
                header = ["index_id"]
                if id_mapping:
                    header.append("mapped_id")
                header.extend([f"dim_{i}" for i in range(min(10, index.d))])
                writer.writerow(header)
                
                # Write sample data
                for i in range(sample_size):
                    row = [i]
                    if id_mapping and i in id_mapping:
                        row.append(str(id_mapping[i])[:100])
                    row.extend(vectors[i][:10].tolist())
                    writer.writerow(row)

    return {
        "index": index,
        "vectors": vectors,
        "metadata": metadata,
        "id_mapping": id_mapping
    }

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Inspect and dump FAISS index content")
    parser.add_argument("index_path", help="Path to the FAISS index file (.faiss)")
    parser.add_argument("--output", "-o", help="Directory to save output files")
    
    args = parser.parse_args()
    inspect_faiss_index(args.index_path, args.output)
