#!/usr/bin/env bash
# Build FAISS index from NDJSON knowledge base
# Usage:
#   scripts/local/build_faiss.sh [tenant_id] [ndjson_path]
#
# Examples:
#   scripts/local/build_faiss.sh my-tenant data/my_kb.ndjson
#   scripts/local/build_faiss.sh   # Uses defaults

set -euo pipefail

# Project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
cd "${REPO_ROOT}"

# Arguments with defaults
TENANT_ID="${1:-default}"
NDJSON_PATH="${2:-data/kb_sample.ndjson}"

# Load .env if present
if [[ -f ".env" ]]; then
  # shellcheck disable=SC2046
  export $(grep -v '^#' .env | xargs)
fi

# Set defaults
: "${MSP_OFFLINE:=1}"
: "${MSP_EMBEDDING_MODEL:=sentence-transformers/all-MiniLM-L6-v2}"
: "${MSP_EMBEDDING_CACHE_DIR:=artifacts/emb}"
: "${MSP_FAISS_INDEX_DIR:=.codex/tenants}"

export MSP_OFFLINE

echo "==================================="
echo "FAISS Index Builder"
echo "==================================="
echo "Repository:      ${REPO_ROOT}"
echo "Tenant ID:       ${TENANT_ID}"
echo "NDJSON Path:     ${NDJSON_PATH}"
echo "Embedding Model: ${MSP_EMBEDDING_MODEL}"
echo "Offline Mode:    ${MSP_OFFLINE}"
echo ""

# Check if input file exists
if [[ ! -f "${NDJSON_PATH}" ]]; then
    echo "Warning: NDJSON file not found: ${NDJSON_PATH}"
    echo ""
    echo "Creating sample KB file..."
    
    # Create sample data directory
    mkdir -p "$(dirname "${NDJSON_PATH}")"
    
    # Create sample NDJSON file
    cat > "${NDJSON_PATH}" <<'EOF'
{"id": "doc1", "content": "Machine learning is a subset of artificial intelligence that focuses on the development of algorithms that can learn from and make predictions on data.", "metadata": {"source": "ml_basics"}}
{"id": "doc2", "content": "Natural language processing (NLP) is a field of AI that focuses on the interaction between computers and human language.", "metadata": {"source": "nlp_intro"}}
{"id": "doc3", "content": "Deep learning is a type of machine learning that uses neural networks with multiple layers to learn hierarchical representations of data.", "metadata": {"source": "dl_overview"}}
{"id": "doc4", "content": "Retrieval-augmented generation (RAG) combines retrieval systems with generative models to produce more accurate and contextual responses.", "metadata": {"source": "rag_guide"}}
{"id": "doc5", "content": "Vector databases store embeddings and enable efficient similarity search for semantic retrieval tasks.", "metadata": {"source": "vector_db_intro"}}
EOF
    
    echo "Sample KB created at ${NDJSON_PATH}"
    echo ""
fi

# Verify file is readable
if [[ ! -r "${NDJSON_PATH}" ]]; then
    echo "Error: Cannot read file: ${NDJSON_PATH}"
    exit 1
fi

# Create output directory
INDEX_DIR="${MSP_FAISS_INDEX_DIR}/${TENANT_ID}/faiss"
mkdir -p "${INDEX_DIR}"
mkdir -p "${MSP_EMBEDDING_CACHE_DIR}"

echo "Building embeddings and FAISS index..."
echo "Output directory: ${INDEX_DIR}"
echo ""

# Check for Python and required modules
if ! command -v python3 &> /dev/null; then
    echo "Error: python3 not found"
    exit 1
fi

# Build index using Python
python3 <<PYEOF
import sys
sys.path.insert(0, '.')

try:
    from src.codex.retrieval import build_embeddings
    from src.codex.retrieval.stores import FAISSStore
    
    print('Loading documents from ${NDJSON_PATH}...')
    embeddings, documents = build_embeddings(
        ndjson_path='${NDJSON_PATH}',
        model_name='${MSP_EMBEDDING_MODEL}',
        cache_dir='${MSP_EMBEDDING_CACHE_DIR}',
        batch_size=32,
    )
    
    print(f'Creating FAISS index for {len(documents)} documents...')
    store = FAISSStore(index_dir='${INDEX_DIR}', index_name='default')
    store.create_index(embeddings, documents)
    
    print('Saving index...')
    store.save()
    
    print('')
    print('✓ FAISS index built successfully!')
    print(f'  - Tenant:    ${TENANT_ID}')
    print(f'  - Documents: {len(documents)}')
    print(f'  - Dimension: {embeddings.shape[1]}')
    print(f'  - Location:  ${INDEX_DIR}')
    
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
