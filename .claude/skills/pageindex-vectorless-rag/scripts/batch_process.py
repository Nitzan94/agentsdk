#!/usr/bin/env python3
"""
Batch process multiple PDF documents using PageIndex SDK.

Usage:
    python batch_process.py <directory> [--api-key YOUR_KEY] [--output results.json]
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path
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
            return result

        if time.time() - start_time > timeout:
            return {"status": "timeout", "error": f"Timeout after {timeout}s"}

        time.sleep(interval)


def process_document(pi_client, pdf_path):
    """Process single document and return metadata."""
    try:
        print(f"[INFO] Processing: {pdf_path}")

        # Submit
        result = pi_client.submit_document(pdf_path)
        doc_id = result["doc_id"]

        # Wait for OCR
        ocr_result = wait_for_completion(lambda: pi_client.get_ocr(doc_id))
        if ocr_result.get("status") != "completed":
            return {
                "file": str(pdf_path),
                "status": "failed",
                "error": f"OCR failed: {ocr_result.get('error', 'Unknown')}"
            }

        # Wait for tree
        tree_result = wait_for_completion(lambda: pi_client.get_tree(doc_id))
        if tree_result.get("status") != "completed":
            return {
                "file": str(pdf_path),
                "status": "failed",
                "error": f"Tree generation failed: {tree_result.get('error', 'Unknown')}"
            }

        tree = tree_result.get("result", [])
        print(f"[OK] {pdf_path.name}: {len(tree)} nodes")

        return {
            "file": str(pdf_path),
            "doc_id": doc_id,
            "status": "completed",
            "tree_nodes": len(tree),
            "retrieval_ready": pi_client.is_retrieval_ready(doc_id)
        }

    except Exception as e:
        print(f"[ERROR] {pdf_path.name}: {str(e)}")
        return {
            "file": str(pdf_path),
            "status": "error",
            "error": str(e)
        }


def main():
    parser = argparse.ArgumentParser(description="Batch process PDFs with PageIndex")
    parser.add_argument("directory", help="Directory containing PDF files")
    parser.add_argument("--api-key", help="PageIndex API key (or set PAGEINDEX_API_KEY)")
    parser.add_argument("--output", default="pageindex_results.json", help="Output JSON file")
    parser.add_argument("--pattern", default="*.pdf", help="File pattern to match")
    args = parser.parse_args()

    # Get API key
    api_key = args.api_key or os.environ.get("PAGEINDEX_API_KEY")
    if not api_key:
        print("[ERROR] API key required")
        sys.exit(1)

    # Initialize client
    print("[INFO] Initializing PageIndex client...")
    pi_client = PageIndexClient(api_key=api_key)

    # Find PDFs
    directory = Path(args.directory)
    if not directory.exists():
        print(f"[ERROR] Directory not found: {directory}")
        sys.exit(1)

    pdf_files = list(directory.glob(args.pattern))
    if not pdf_files:
        print(f"[ERROR] No files matching {args.pattern} in {directory}")
        sys.exit(1)

    print(f"[INFO] Found {len(pdf_files)} files to process\n")

    # Process each file
    results = []
    for i, pdf_path in enumerate(pdf_files, 1):
        print(f"[{i}/{len(pdf_files)}] {pdf_path.name}")
        result = process_document(pi_client, pdf_path)
        results.append(result)
        print()

    # Save results
    output_path = Path(args.output)
    with open(output_path, 'w') as f:
        json.dump({
            "total_files": len(pdf_files),
            "completed": sum(1 for r in results if r["status"] == "completed"),
            "failed": sum(1 for r in results if r["status"] != "completed"),
            "results": results
        }, f, indent=2)

    print(f"[OK] Results saved to: {output_path}")

    # Summary
    completed = [r for r in results if r["status"] == "completed"]
    failed = [r for r in results if r["status"] != "completed"]

    print(f"\n[SUMMARY]")
    print(f"Total: {len(results)}")
    print(f"Completed: {len(completed)}")
    print(f"Failed: {len(failed)}")

    if completed:
        print("\n[COMPLETED]")
        for r in completed:
            print(f"  - {Path(r['file']).name}: {r['doc_id']}")

    if failed:
        print("\n[FAILED]")
        for r in failed:
            print(f"  - {Path(r['file']).name}: {r.get('error', 'Unknown error')}")


if __name__ == "__main__":
    main()
