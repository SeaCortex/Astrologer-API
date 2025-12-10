#!/usr/bin/env python3
"""
Generate RapidAPI OpenAPI Spec

This script creates a customized OpenAPI JSON file for RapidAPI by:
1. Reading the base openapi.json file
2. Reading markdown documentation files from RapidAPI_Docs/
3. Replacing operationId and description in the OpenAPI spec
4. Writing the result to rapidapi.json

Usage:
    python scripts/generate_rapidapi_docs.py

Markdown Format Expected:
    ## Endpoint
    /api/v5/chart/birth-chart

    ## Name
    Birth Chart

    ## Description
    Full description text...

    ### Parameters
    - param1: description
    - param2: description
"""

import json
import re
from pathlib import Path


# =============================================================================
# CONFIGURATION
# =============================================================================

# Project root directory (parent of scripts/)
PROJECT_ROOT = Path(__file__).parent.parent

# Input files
OPENAPI_FILE = PROJECT_ROOT / "openapi.json"
RAPIDAPI_DOCS_DIR = PROJECT_ROOT / "RapidAPI_Docs"

# Output file
OUTPUT_FILE = PROJECT_ROOT / "rapidapi.json"


# =============================================================================
# STEP 1: READ OPENAPI.JSON
# =============================================================================

def load_openapi() -> dict:
    """Load the base OpenAPI specification from openapi.json."""
    print(f"Loading: {OPENAPI_FILE}")
    
    with open(OPENAPI_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    print(f"  Found {len(data.get('paths', {}))} endpoints")
    return data


# =============================================================================
# STEP 2: PARSE MARKDOWN DOCUMENTATION FILES
# =============================================================================

def extract_endpoint(content: str) -> str | None:
    """
    Extract the endpoint path from markdown content.
    
    Looks for:
        ## Endpoint
        /api/v5/chart/birth-chart
    """
    match = re.search(r"## Endpoint\s*\n(.+)", content)
    if match:
        return match.group(1).strip()
    return None


def extract_name(content: str) -> str | None:
    """
    Extract the operation name from markdown content.
    
    Looks for:
        ## Name
        Birth Chart
    """
    match = re.search(r"## Name\s*\n(.+)", content)
    if match:
        return match.group(1).strip()
    return None


def extract_description(content: str) -> str:
    """
    Extract the description (including ### Parameters) from markdown content.
    
    Looks for:
        ## Description
        Full description text...
        
        ### Parameters
        - param1: description
    
    Stops at the next ## section (but keeps ### subsections).
    """
    match = re.search(r"## Description\s*\n(.*?)(?=\n## (?!#)|$)", content, re.DOTALL)
    if match:
        return match.group(1).strip()
    return ""


def parse_markdown_file(file_path: Path) -> dict | None:
    """
    Parse a single markdown documentation file.
    
    Returns a dict with: endpoint, name, description
    Or None if required fields are missing.
    """
    content = file_path.read_text(encoding="utf-8")
    
    endpoint = extract_endpoint(content)
    name = extract_name(content)
    description = extract_description(content)
    
    # Validate required fields
    if not endpoint:
        print(f"  WARNING: No endpoint in {file_path.name}")
        return None
    
    if not name:
        print(f"  WARNING: No name in {file_path.name}")
        return None
    
    return {
        "endpoint": endpoint,
        "name": name,
        "description": description,
        "source": file_path.name,
    }


def load_all_markdown_docs() -> list[dict]:
    """
    Load and parse all markdown files from RapidAPI_Docs directory.
    
    Returns a list of parsed documentation dictionaries.
    """
    print(f"\nLoading markdown files from: {RAPIDAPI_DOCS_DIR}")
    
    docs = []
    
    # Find all .md files recursively
    md_files = sorted(RAPIDAPI_DOCS_DIR.rglob("*.md"))
    
    for md_file in md_files:
        parsed = parse_markdown_file(md_file)
        if parsed:
            docs.append(parsed)
            print(f"  Parsed: {md_file.relative_to(RAPIDAPI_DOCS_DIR)}")
    
    print(f"  Total: {len(docs)} documentation files")
    return docs


# =============================================================================
# STEP 3: UPDATE OPENAPI SPEC
# =============================================================================

def find_operation_in_openapi(openapi_data: dict, endpoint: str) -> dict | None:
    """
    Find the operation object for a given endpoint path.
    
    Returns the operation dict (e.g., the "post" object) or None if not found.
    """
    paths = openapi_data.get("paths", {})
    
    # Look for the endpoint in paths
    if endpoint not in paths:
        return None
    
    path_item = paths[endpoint]
    
    # Return the first HTTP method found (usually "post" for this API)
    for method in ["post", "get", "put", "delete", "patch"]:
        if method in path_item:
            return path_item[method]
    
    return None


def update_openapi_with_docs(openapi_data: dict, docs: list[dict]) -> int:
    """
    Update the OpenAPI spec with documentation from markdown files.
    
    For each doc:
    - Find the matching endpoint in OpenAPI
    - Set operationId = doc["name"] (exactly as-is)
    - Set description = doc["description"]
    
    Returns the number of endpoints updated.
    """
    print("\nUpdating OpenAPI spec:")
    
    updated_count = 0
    
    for doc in docs:
        endpoint = doc["endpoint"]
        new_name = doc["name"]
        new_description = doc["description"]
        
        # Find the operation in OpenAPI
        operation = find_operation_in_openapi(openapi_data, endpoint)
        
        if operation is None:
            print(f"  NOT FOUND: {endpoint}")
            continue
        
        # Get old values for logging
        old_operation_id = operation.get("operationId", "")
        
        # Update operationId (use name exactly as-is)
        operation["operationId"] = new_name
        
        # Update description
        operation["description"] = new_description
        
        # Log the change
        print(f"  Updated: {endpoint}")
        print(f"           operationId: {old_operation_id!r} -> {new_name!r}")
        
        updated_count += 1
    
    return updated_count


# =============================================================================
# STEP 4: WRITE OUTPUT FILE
# =============================================================================

def save_rapidapi_json(openapi_data: dict) -> None:
    """Save the modified OpenAPI spec to rapidapi.json."""
    print(f"\nWriting: {OUTPUT_FILE}")
    
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(openapi_data, f, indent=2, ensure_ascii=False)
    
    print("  Done!")


# =============================================================================
# MAIN
# =============================================================================

def main() -> None:
    """
    Main entry point.
    
    Steps:
    1. Load openapi.json
    2. Parse all markdown docs from RapidAPI_Docs/
    3. Update operationId and description for each endpoint
    4. Write rapidapi.json
    """
    print("=" * 60)
    print("Generate RapidAPI OpenAPI Spec")
    print("=" * 60)
    
    # Step 1: Load base OpenAPI spec
    openapi_data = load_openapi()
    
    # Step 2: Load all markdown documentation
    docs = load_all_markdown_docs()
    
    # Step 3: Update OpenAPI with documentation
    updated_count = update_openapi_with_docs(openapi_data, docs)
    
    # Step 4: Write output
    save_rapidapi_json(openapi_data)
    
    # Summary
    print("\n" + "=" * 60)
    print("Summary:")
    print(f"  Documentation files: {len(docs)}")
    print(f"  Endpoints updated:   {updated_count}")
    print(f"  Output file:         {OUTPUT_FILE.name}")
    print("=" * 60)


if __name__ == "__main__":
    main()
