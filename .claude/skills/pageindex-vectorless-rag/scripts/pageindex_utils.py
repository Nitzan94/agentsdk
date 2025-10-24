"""
Utility functions for PageIndex SDK operations.

Common helper functions for document processing, polling, and result formatting.
"""

import time
from typing import Callable, Dict, Any, Optional


def wait_for_status(
    check_fn: Callable[[], Dict[str, Any]],
    target_status: str = "completed",
    interval: int = 3,
    timeout: int = 300,
    verbose: bool = True
) -> Dict[str, Any]:
    """
    Poll a status-checking function until target status or timeout.

    Args:
        check_fn: Function that returns status dict
        target_status: Status to wait for (default: "completed")
        interval: Seconds between checks
        timeout: Maximum seconds to wait
        verbose: Print status updates

    Returns:
        Final result dict

    Raises:
        TimeoutError: If timeout reached
        Exception: If status becomes "failed"
    """
    start_time = time.time()
    attempts = 0

    while True:
        attempts += 1
        result = check_fn()
        status = result.get("status")

        if status == target_status:
            if verbose:
                print(f"[OK] Completed after {attempts} attempts")
            return result

        if status == "failed":
            error = result.get("error", "Unknown error")
            raise Exception(f"Operation failed: {error}")

        elapsed = time.time() - start_time
        if elapsed > timeout:
            raise TimeoutError(f"Timeout after {timeout}s (status: {status})")

        if verbose:
            print(f"[INFO] Status: {status}, elapsed: {int(elapsed)}s")

        time.sleep(interval)


def format_retrieval_results(retrieval_result: Dict[str, Any]) -> str:
    """
    Format retrieval results for human-readable display.

    Args:
        retrieval_result: Result from get_retrieval_result()

    Returns:
        Formatted string with nodes and content
    """
    if retrieval_result.get("status") != "completed":
        return f"Status: {retrieval_result.get('status')}"

    nodes = retrieval_result.get("retrieved_nodes", [])
    if not nodes:
        return "No results found"

    output = []
    output.append(f"Query: {retrieval_result.get('query', 'N/A')}")
    output.append(f"Retrieved {len(nodes)} nodes:\n")

    for i, node in enumerate(nodes, 1):
        output.append(f"{i}. {node['title']} (Node: {node['node_id']})")

        for content in node.get('relevant_contents', []):
            page = content['page_index']
            text = content['relevant_content']
            output.append(f"   [Page {page}] {text[:150]}...")

        output.append("")

    return "\n".join(output)


def get_tree_summary(tree_result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract summary statistics from tree result.

    Args:
        tree_result: Result from get_tree()

    Returns:
        Dict with tree statistics
    """
    if tree_result.get("status") != "completed":
        return {"status": tree_result.get("status")}

    tree = tree_result.get("result", [])

    def count_nodes(nodes):
        count = len(nodes)
        for node in nodes:
            if "nodes" in node:
                count += count_nodes(node["nodes"])
        return count

    def max_depth(nodes, depth=0):
        if not nodes:
            return depth
        return max(max_depth(node.get("nodes", []), depth + 1) for node in nodes)

    total_nodes = count_nodes(tree)
    tree_depth = max_depth(tree)

    return {
        "status": "completed",
        "top_level_nodes": len(tree),
        "total_nodes": total_nodes,
        "max_depth": tree_depth,
        "node_titles": [node.get("title", "Untitled") for node in tree]
    }


def extract_pages_from_ocr(ocr_result: Dict[str, Any], format_type: str = "page") -> list:
    """
    Extract page data from OCR result.

    Args:
        ocr_result: Result from get_ocr()
        format_type: OCR format used ("page", "node", "raw")

    Returns:
        List of page dicts or formatted data
    """
    if ocr_result.get("status") != "completed":
        return []

    result = ocr_result.get("result", [])

    if format_type == "raw":
        return [{"text": result}]

    if format_type == "page":
        return result

    if format_type == "node":
        # Extract pages from hierarchical structure
        pages = []

        def extract_from_nodes(nodes):
            for node in nodes:
                if "page_index" in node:
                    pages.append({
                        "page_index": node["page_index"],
                        "text": node.get("text", "")
                    })
                if "nodes" in node:
                    extract_from_nodes(node["nodes"])

        extract_from_nodes(result)
        return pages

    return []


def create_doc_id_mapping(results: list) -> Dict[str, str]:
    """
    Create filename -> doc_id mapping from batch processing results.

    Args:
        results: List of processing results from batch_process.py

    Returns:
        Dict mapping filenames to doc_ids
    """
    from pathlib import Path

    mapping = {}
    for result in results:
        if result.get("status") == "completed":
            filename = Path(result["file"]).name
            mapping[filename] = result["doc_id"]

    return mapping
