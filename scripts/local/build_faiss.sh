#!/bin/bash
# Build FAISS index from NDJSON knowledge base
# Usage: bash scripts/local/build_faiss.sh <tenant_id> <ndjson_path>

set -e

TENANT_ID="${1:-default}"
NDJSON_PATH="${2:-data/kb_sample.ndjson}"

echo "==================================="
echo "FAISS Index Builder"
echo "==================================="
echo "Tenant ID: ${TENANT_ID}"
echo "NDJSON Path: ${NDJSON_PATH}"
echo ""

# Check if input file exists
if [ ! -f "${NDJSON_PATH}" ]; then
    echo "Error: NDJSON file not found: ${NDJSON_PATH}"
    echo ""
    echo "Creating sample KB file..."
    
    # Create sample data directory
    mkdir -p data
    
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

# Set environment
export MSP_OFFLINE=1

# Create output directory
INDEX_DIR=".codex/tenants/${TENANT_ID}/faiss"
mkdir -p "${INDEX_DIR}"

echo "Building embeddings and FAISS index..."
echo "Output directory: ${INDEX_DIR}"
echo ""

# Build index using Python
python3 -c "
import sys
sys.path.insert(0, '.')

from src.codex.retrieval import build_embeddings
from src.codex.retrieval.stores import FAISSStore

print('Loading documents from ${NDJSON_PATH}...')
embeddings, documents = build_embeddings(
    ndjson_path='${NDJSON_PATH}',
    model_name='sentence-transformers/all-MiniLM-L6-v2',
    cache_dir='artifacts/emb',
    batch_size=32,
)

print(f'Creating FAISS index for {len(documents)} documents...')
store = FAISSStore(index_dir='${INDEX_DIR}', index_name='default')
store.create_index(embeddings, documents)

print('Saving index...')
store.save()

print('')
print('✓ FAISS index built successfully!')
print(f'  - Documents: {len(documents)}')
print(f'  - Dimension: {embeddings.shape[1]}')
print(f'  - Location: ${INDEX_DIR}')
"

echo ""
echo "==================================="
echo "Index build complete!"
echo "==================================="
