#!/usr/bin/env bash
# Build FAISS index from repository documentation or NDJSON
# Usage:
#   scripts/local/build_faiss.sh [tenant_id] [source_type] [path]
#
# Examples:
#   scripts/local/build_faiss.sh default docs .        # Index markdown files
#   scripts/local/build_faiss.sh my-tenant ndjson data/kb.ndjson  # Index NDJSON

set -euo pipefail

# Project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
cd "${REPO_ROOT}"

# Arguments with defaults
TENANT_ID="${1:-default}"
SOURCE_TYPE="${2:-docs}"  # 'docs' or 'ndjson'
SOURCE_PATH="${3:-.}"

# Load .env if present
if [[ -f ".env" ]]; then
  # shellcheck disable=SC2046
  export $(grep -v '^#' .env | xargs)
fi

# Set defaults
: "${MSP_EMBEDDING_MODEL:=sentence-transformers/all-MiniLM-L6-v2}"
: "${MSP_FAISS_INDEX_DIR:=.codex/tenants}"
: "${CHUNK_SIZE:=1000}"
: "${OVERLAP:=128}"

echo "==================================="
echo "FAISS Index Builder (Expanded Context)"
echo "==================================="
echo "Repository:      ${REPO_ROOT}"
echo "Tenant ID:       ${TENANT_ID}"
echo "Source Type:     ${SOURCE_TYPE}"
echo "Source Path:     ${SOURCE_PATH}"
echo "Embedding Model: ${MSP_EMBEDDING_MODEL}"
echo "Chunk Size:      ${CHUNK_SIZE}"
echo "Overlap:         ${OVERLAP}"
echo ""

# Create output directory
mkdir -p "${MSP_FAISS_INDEX_DIR}"

# Check for Python and required modules
if ! command -v python3 &> /dev/null; then
    echo "Error: python3 not found"
    exit 1
fi

echo "Building embeddings and FAISS index..."
echo ""

# Build index using Python with new RAG modules
if [[ "${SOURCE_TYPE}" == "docs" ]]; then
    # Export variables as environment variables for safe access in Python
    export BUILD_TENANT_ID="${TENANT_ID}"
    export BUILD_INDEX_DIR="${MSP_FAISS_INDEX_DIR}"
    export BUILD_CHUNK_SIZE="${CHUNK_SIZE}"
    export BUILD_OVERLAP="${OVERLAP}"
    export BUILD_SOURCE_PATH="${SOURCE_PATH}"
    
    python3 <<'PYEOF'
import sys
import os
from pathlib import Path
sys.path.insert(0, '.')

try:
    from src.codex.rag.indexer import build_index_from_files
    
    # Safely retrieve values from environment variables
    tenant_id = os.environ.get('BUILD_TENANT_ID', 'default')
    index_dir = os.environ.get('BUILD_INDEX_DIR', '.codex/tenants')
    chunk_size = int(os.environ.get('BUILD_CHUNK_SIZE', '1000'))
    overlap = int(os.environ.get('BUILD_OVERLAP', '128'))
    source_path_str = os.environ.get('BUILD_SOURCE_PATH', '.')
    
    # Collect documentation files
    source_path = Path(source_path_str)
    files = []
    
    if source_path.is_file():
        files.append(source_path)
    elif source_path.is_dir():
        # Collect markdown, text, and RST files
        files.extend(source_path.rglob('*.md'))
        files.extend(source_path.rglob('*.txt'))
        files.extend(source_path.rglob('*.rst'))
        
        # Filter out common non-doc directories
        exclude_patterns = ['node_modules', '.git', '__pycache__', 'venv', '.venv']
        files = [f for f in files if not any(ex in str(f) for ex in exclude_patterns)]
    
    if not files:
        print('No files found to index', file=sys.stderr)
        sys.exit(1)
    
    print(f'Found {len(files)} files to index')
    
    # Build index
    index_path = build_index_from_files(
        files=files,
        index_name='docs',
        tenant_id=tenant_id,
        index_dir=index_dir,
        chunk_size=chunk_size,
        overlap=overlap,
    )
    
    print('')
    print('✓ FAISS index built successfully!')
    print(f'  - Tenant:    {tenant_id}')
    print(f'  - Files:     {len(files)}')
    print(f'  - Location:  {index_path}')
    
except ImportError as e:
    print(f'Error: Missing required Python packages: {e}', file=sys.stderr)
    print('Install with: pip install sentence-transformers faiss-cpu', file=sys.stderr)
    sys.exit(1)
except Exception as e:
    print(f'Error building index: {e}', file=sys.stderr)
    import traceback
    traceback.print_exc()
    sys.exit(1)
PYEOF

elif [[ "${SOURCE_TYPE}" == "ndjson" ]]; then
    # For NDJSON, use the old retrieval module if available
    # Or implement NDJSON support in new indexer
    # Export variables as environment variables for safe access in Python
    export BUILD_SOURCE_PATH="${SOURCE_PATH}"
    export BUILD_MSP_EMBEDDING_MODEL="${MSP_EMBEDDING_MODEL}"
    export BUILD_MSP_FAISS_INDEX_DIR="${MSP_FAISS_INDEX_DIR}"
    export BUILD_TENANT_ID="${TENANT_ID}"
    
    python3 <<'PYEOF'
import sys
import os
sys.path.insert(0, '.')

try:
    from src.codex.retrieval.embed import build_embeddings
    from src.codex.retrieval.stores import FAISSStore
    
    # Safely retrieve values from environment variables
    source_path = os.environ.get('BUILD_SOURCE_PATH', '.')
    embedding_model = os.environ.get('BUILD_MSP_EMBEDDING_MODEL', 'sentence-transformers/all-MiniLM-L6-v2')
    faiss_index_dir = os.environ.get('BUILD_MSP_FAISS_INDEX_DIR', '.codex/tenants')
    tenant_id = os.environ.get('BUILD_TENANT_ID', 'default')
    
    print(f'Loading documents from {source_path}...')
    embeddings, documents = build_embeddings(
        ndjson_path=source_path,
        model_name=embedding_model,
        batch_size=32,
    )
    
    print(f'Creating FAISS index for {len(documents)} documents...')
    index_dir = f'{faiss_index_dir}/{tenant_id}/faiss'
    os.makedirs(index_dir, exist_ok=True)
    
    store = FAISSStore(index_dir=index_dir, index_name='default')
    store.create_index(embeddings, documents)
    
    print('Saving index...')
    store.save()
    
    print('')
    print('✓ FAISS index built successfully!')
    print(f'  - Tenant:    {tenant_id}')
    print(f'  - Documents: {len(documents)}')
    print(f'  - Dimension: {embeddings.shape[1]}')
    print(f'  - Location:  {index_dir}')
    
except ImportError as e:
    print(f'Error: Missing required Python packages: {e}', file=sys.stderr)
    print('Install with: pip install sentence-transformers faiss-cpu', file=sys.stderr)
    sys.exit(1)
except Exception as e:
    print(f'Error building index: {e}', file=sys.stderr)
    import traceback
    traceback.print_exc()
    sys.exit(1)
PYEOF

else
    echo "Error: Unknown source type '${SOURCE_TYPE}'. Use 'docs' or 'ndjson'."
    exit 1
fi

EXIT_CODE=$?

echo ""
if [[ ${EXIT_CODE} -eq 0 ]]; then
    echo "==================================="
    echo "Index build complete!"
    echo "==================================="
else
    echo "==================================="
    echo "Index build failed!"
    echo "==================================="
    exit ${EXIT_CODE}
fi
