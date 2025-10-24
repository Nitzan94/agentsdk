#!/usr/bin/env python3
"""
Process a PDF document using PageIndex SDK.

Usage:
    python process_document.py <pdf_path> [--api-key YOUR_KEY] [--query "Your question"]
"""

import argparse
import os
import sys
import time
from pageindex import PageIndexClient


def wait_for_completion(check_fn, interval=3, timeout=300):
    """Poll until completion or timeout."""
    start_time = time.time()
    while True:
        result = check_fn()
        status = result.get("status")

        if status == "completed":
            return result
        elif status == "failed":
            raise Exception(f"Processing failed: {result.get('error', 'Unknown error')}")

        if time.time() - start_time > timeout:
            raise TimeoutError(f"Processing timed out after {timeout} seconds")

        print(f"Status: {status}, waiting {interval}s...")
        time.sleep(interval)


def main():
    parser = argparse.ArgumentParser(description="Process PDF with PageIndex")
    parser.add_argument("pdf_path", help="Path to PDF file")
    parser.add_argument("--api-key", help="PageIndex API key (or set PAGEINDEX_API_KEY env var)")
    parser.add_argument("--query", help="Optional query to run after processing")
    parser.add_argument("--thinking", action="store_true", help="Enable deeper retrieval")
    args = parser.parse_args()

    # Get API key
    api_key = args.api_key or os.environ.get("PAGEINDEX_API_KEY")
    if not api_key:
        print("[ERROR] API key required via --api-key or PAGEINDEX_API_KEY env var")
        sys.exit(1)

    # Initialize client
    print(f"[INFO] Initializing PageIndex client...")
    pi_client = PageIndexClient(api_key=api_key)

    # Submit document
    print(f"[INFO] Submitting document: {args.pdf_path}")
    result = pi_client.submit_document(args.pdf_path)
    doc_id = result["doc_id"]
    print(f"[INFO] Document ID: {doc_id}")

    # Wait for OCR
    print("[INFO] Waiting for OCR processing...")
    ocr_result = wait_for_completion(lambda: pi_client.get_ocr(doc_id))
    print("[OK] OCR completed")

    # Wait for tree generation
    print("[INFO] Waiting for tree generation...")
    tree_result = wait_for_completion(lambda: pi_client.get_tree(doc_id))
    print("[OK] Tree generation completed")

    tree = tree_result.get("result", [])
    print(f"[INFO] Tree contains {len(tree)} top-level nodes")

    # Query if requested
    if args.query:
        print(f"[INFO] Querying: {args.query}")

        if not pi_client.is_retrieval_ready(doc_id):
            print("[ERROR] Document not ready for retrieval")
            sys.exit(1)

        retrieval = pi_client.submit_retrieval_query(
            doc_id=doc_id,
            query=args.query,
            thinking=args.thinking
        )
        retrieval_id = retrieval["retrieval_id"]

        print("[INFO] Waiting for retrieval results...")
        retrieval_result = wait_for_completion(
            lambda: pi_client.get_retrieval_result(retrieval_id),
            interval=2
        )

        nodes = retrieval_result.get("retrieved_nodes", [])
        print(f"\n[OK] Retrieved {len(nodes)} relevant nodes:\n")

        for i, node in enumerate(nodes, 1):
            print(f"{i}. {node['title']} (Node ID: {node['node_id']})")
            for content in node.get('relevant_contents', []):
                print(f"   Page {content['page_index']}:")
                print(f"   {content['relevant_content'][:200]}...")
            print()

    print(f"\n[OK] Processing complete. Document ID: {doc_id}")
    print(f"[INFO] Save this ID to query the document later without reprocessing.")


if __name__ == "__main__":
    main()
