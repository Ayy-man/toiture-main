"""Detect near-duplicate materials using fuzzy string matching.

Usage:
    python -m app.scripts.detect_duplicates [--threshold 85] [--dry-run] [--output report.csv]

Environment variables required:
    SUPABASE_URL
    SUPABASE_SERVICE_ROLE_KEY
"""

import argparse
import csv
import logging
import os
import sys
from collections import defaultdict
from typing import Optional

from dotenv import load_dotenv
from rapidfuzz import fuzz
from supabase import Client, create_client

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def get_supabase_client() -> Optional[Client]:
    """Create Supabase client from environment variables."""
    supabase_url = os.environ.get("SUPABASE_URL")
    supabase_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

    if not supabase_url or not supabase_key:
        logger.error(
            "ERROR: SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set.\n"
            "Please configure these environment variables and try again."
        )
        return None

    return create_client(supabase_url, supabase_key)


def load_materials(client: Client) -> list[dict]:
    """Load all materials from Supabase where item_type='material'."""
    logger.info("Loading materials from Supabase...")
    response = client.from_("materials").select("id, name").eq("item_type", "material").execute()
    materials = response.data
    logger.info(f"Loaded {len(materials)} materials")
    return materials


def find_duplicates(materials: list[dict], threshold: int = 85) -> list[dict]:
    """Find near-duplicate materials using fuzzy string matching.

    Args:
        materials: List of material dicts with 'id' and 'name'
        threshold: Similarity threshold (0-100)

    Returns:
        List of duplicate pairs with similarity scores
    """
    logger.info(f"Comparing materials with threshold {threshold}...")
    duplicates = []

    for i in range(len(materials)):
        for j in range(i + 1, len(materials)):
            mat1 = materials[i]
            mat2 = materials[j]

            # Calculate similarity score
            score = fuzz.token_sort_ratio(mat1["name"], mat2["name"])

            if score >= threshold:
                duplicates.append(
                    {
                        "score": score,
                        "id1": mat1["id"],
                        "name1": mat1["name"],
                        "id2": mat2["id"],
                        "name2": mat2["name"],
                    }
                )

    logger.info(f"Found {len(duplicates)} duplicate pairs")
    return duplicates


def cluster_duplicates(duplicates: list[dict]) -> list[list[int]]:
    """Group duplicate pairs into clusters.

    If A~B and B~C, group all three together.

    Returns:
        List of clusters (each cluster is a list of material IDs)
    """
    # Build adjacency graph
    graph = defaultdict(set)
    for dup in duplicates:
        id1, id2 = dup["id1"], dup["id2"]
        graph[id1].add(id2)
        graph[id2].add(id1)

    # Find connected components using DFS
    visited = set()
    clusters = []

    def dfs(node: int, cluster: list[int]) -> None:
        visited.add(node)
        cluster.append(node)
        for neighbor in graph[node]:
            if neighbor not in visited:
                dfs(neighbor, cluster)

    for node in graph:
        if node not in visited:
            cluster = []
            dfs(node, cluster)
            clusters.append(sorted(cluster))

    return clusters


def print_report(duplicates: list[dict], clusters: list[list[int]], materials_dict: dict) -> None:
    """Print duplicate detection report to stdout."""
    print("\n" + "=" * 80)
    print("DUPLICATE DETECTION REPORT")
    print("=" * 80)

    if not duplicates:
        print("\nNo duplicates found!")
        return

    print(f"\nFound {len(duplicates)} duplicate pairs in {len(clusters)} clusters\n")

    # Print by cluster
    for i, cluster in enumerate(clusters, 1):
        print(f"\nCluster {i} ({len(cluster)} items):")
        print("-" * 80)
        for mat_id in cluster:
            print(f"  ID {mat_id}: {materials_dict[mat_id]}")

        # Show similarity scores within this cluster
        cluster_set = set(cluster)
        cluster_dups = [
            d for d in duplicates if d["id1"] in cluster_set and d["id2"] in cluster_set
        ]
        print("\n  Similarity scores:")
        for dup in cluster_dups:
            print(f"    {dup['score']}% - ID {dup['id1']} ↔ ID {dup['id2']}")

    print("\n" + "=" * 80)


def save_report_csv(duplicates: list[dict], output_path: str) -> None:
    """Save duplicate pairs to CSV file."""
    logger.info(f"Saving report to {output_path}")
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f, fieldnames=["score", "id1", "name1", "id2", "name2"]
        )
        writer.writeheader()
        writer.writerows(duplicates)
    logger.info(f"Report saved to {output_path}")


def flag_duplicates_in_db(client: Client, duplicates: list[dict], dry_run: bool = True) -> None:
    """Update review_status='duplicate' for duplicate materials.

    Flags both items in each pair for manual review.
    """
    if dry_run:
        logger.info("DRY RUN: Would flag the following material IDs as duplicates:")
        all_ids = set()
        for dup in duplicates:
            all_ids.add(dup["id1"])
            all_ids.add(dup["id2"])
        logger.info(f"  {sorted(all_ids)}")
        return

    # Collect all IDs to flag
    ids_to_flag = set()
    for dup in duplicates:
        ids_to_flag.add(dup["id1"])
        ids_to_flag.add(dup["id2"])

    logger.info(f"Flagging {len(ids_to_flag)} materials as duplicates...")

    # Update in batches
    batch_size = 100
    ids_list = list(ids_to_flag)

    for i in range(0, len(ids_list), batch_size):
        batch = ids_list[i : i + batch_size]
        response = (
            client.from_("materials")
            .update({"review_status": "duplicate"})
            .in_("id", batch)
            .execute()
        )
        logger.debug(f"Flagged batch {i // batch_size + 1}")

    logger.info(f"Successfully flagged {len(ids_to_flag)} materials")


def main() -> None:
    """Main deduplication script."""
    parser = argparse.ArgumentParser(description="Detect near-duplicate materials")
    parser.add_argument(
        "--threshold",
        type=int,
        default=85,
        help="Similarity threshold (0-100, default: 85)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print report without updating database",
    )
    parser.add_argument(
        "--output",
        type=str,
        help="Save report to CSV file (optional)",
    )
    args = parser.parse_args()

    # Load environment variables
    load_dotenv()

    # Connect to Supabase
    client = get_supabase_client()
    if not client:
        sys.exit(1)

    try:
        # Load materials
        materials = load_materials(client)

        if not materials:
            logger.warning("No materials found in database")
            return

        # Find duplicates
        duplicates = find_duplicates(materials, threshold=args.threshold)

        if not duplicates:
            logger.info("No duplicates found!")
            return

        # Cluster duplicates
        clusters = cluster_duplicates(duplicates)

        # Build materials dict for printing
        materials_dict = {m["id"]: m["name"] for m in materials}

        # Print report
        print_report(duplicates, clusters, materials_dict)

        # Save to CSV if requested
        if args.output:
            save_report_csv(duplicates, args.output)

        # Flag in database
        flag_duplicates_in_db(client, duplicates, dry_run=args.dry_run)

    except Exception as e:
        logger.error(f"Error during deduplication: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
