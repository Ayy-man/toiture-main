#!/usr/bin/env python3
"""One-time script to upload CBR embeddings to Pinecone.

Usage:
    export PINECONE_API_KEY=your_key
    export PINECONE_INDEX_NAME=toiturelv-cortex  # Optional, defaults to toiturelv-cortex
    python -m scripts.upload_embeddings
"""

import json
import os
from pathlib import Path

import numpy as np
from pinecone import ServerlessSpec
from pinecone.grpc import PineconeGRPC as Pinecone
from tqdm import tqdm

# Find data files relative to project root
PROJECT_ROOT = Path(__file__).parent.parent.parent
DATA_DIR = PROJECT_ROOT / "cortex-data"


def main():
    # Configuration
    api_key = os.environ.get("PINECONE_API_KEY")
    if not api_key:
        print("ERROR: PINECONE_API_KEY environment variable required")
        return

    index_name = os.environ.get("PINECONE_INDEX_NAME", "toiturelv-cortex")

    # Initialize Pinecone
    print("Connecting to Pinecone...")
    pc = Pinecone(api_key=api_key)

    # Create index if it doesn't exist
    existing_indexes = [idx.name for idx in pc.list_indexes()]
    if index_name not in existing_indexes:
        print(f"Creating index '{index_name}'...")
        pc.create_index(
            name=index_name,
            dimension=384,
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region="us-east-1")
        )
        print("Index created. Waiting for it to be ready...")
    else:
        print(f"Index '{index_name}' already exists")

    # Get index host and connect
    index_info = pc.describe_index(index_name)
    index = pc.Index(host=index_info.host)

    # Store host URL for user to add to .env
    print(f"\n*** IMPORTANT: Add this to your .env file ***")
    print(f"PINECONE_INDEX_HOST={index_info.host}")
    print()

    # Load embeddings
    print("Loading embeddings from cortex-data/cbr_embeddings.npz...")
    embeddings_path = DATA_DIR / "cbr_embeddings.npz"
    data = np.load(embeddings_path)
    case_ids = data["case_ids"]
    embeddings = data["embeddings"]
    print(f"Loaded {len(case_ids)} embeddings ({embeddings.shape[1]} dimensions)")

    # Load case metadata
    print("Loading case metadata from cortex-data/cbr_cases.json...")
    cases_path = DATA_DIR / "cbr_cases.json"
    with open(cases_path) as f:
        cases_list = json.load(f)
    cases = {str(c["case_id"]): c for c in cases_list}
    print(f"Loaded {len(cases)} cases")

    # Prepare vectors
    print("Preparing vectors with metadata...")
    vectors = []
    for case_id, embedding in zip(case_ids, embeddings):
        case = cases.get(str(case_id), {})
        features = case.get("features", {})
        pricing = case.get("pricing", {})

        # Flatten metadata for Pinecone (max 40KB per record)
        # Remove None values (Pinecone doesn't accept null)
        metadata = {
            "case_id": str(case_id),
            "year": case.get("year"),
            "category": features.get("category", "Unknown"),
            "sqft": features.get("sqft"),
            "total": pricing.get("total"),
            "per_sqft": pricing.get("per_sqft"),
            "material_sell": pricing.get("material_sell"),
            "labor_sell": pricing.get("labor_sell"),
            "complexity_score": features.get("complexity_score"),
        }
        metadata = {k: v for k, v in metadata.items() if v is not None}

        vectors.append({
            "id": str(case_id),
            "values": embedding.tolist(),
            "metadata": metadata
        })

    # Upsert in batches
    batch_size = 500  # Optimal for 384-dim vectors
    print(f"Uploading {len(vectors)} vectors in batches of {batch_size}...")
    for i in tqdm(range(0, len(vectors), batch_size), desc="Uploading"):
        batch = vectors[i:i + batch_size]
        index.upsert(vectors=batch, namespace="cbr")

    # Verify
    print("\nVerifying upload...")
    stats = index.describe_index_stats()
    namespace_count = stats.namespaces.get("cbr", {}).vector_count if stats.namespaces else 0
    print(f"Index stats: {stats}")
    print(f"\nUpload complete! Vectors in 'cbr' namespace: {namespace_count}")

    if namespace_count == len(vectors):
        print("SUCCESS: All vectors uploaded!")
    else:
        print(f"WARNING: Expected {len(vectors)}, got {namespace_count}")


if __name__ == "__main__":
    main()
