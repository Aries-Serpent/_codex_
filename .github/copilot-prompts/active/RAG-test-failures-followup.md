# 🔬 RAG Module Test Failures — Investigation Follow-Up

> **Created:** 2026-04-01 (S266)
> **PR:** #3846 — fix(s265): CSVMetricsWriter export, mypy −36 errors
> **Triage Issue:** [#3844](https://github.com/Aries-Serpent/_codex_/issues/3844)
> **Status:** Partially fixed — remaining failures documented here

---

## 🔧 Fixes Applied in S266 (This Session)

The following were fixed surgically:

| Fix | File | Resolves |
|-----|------|---------|
| `has_meta_tensors` early `nn.Module` check | `src/codex/rag/utils.py` | 4× `test_embeddings_comprehensive` mock failures |
| Added `RAGRetriever` stub class | `src/codex/rag/retriever.py` | `ImportError: cannot import name 'RAGRetriever'` |
| Added `EmbeddingModel` stub class | `src/codex/rag/embeddings.py` | `ImportError: cannot import name 'EmbeddingModel'` |
| Added `model` + `move_to_device()` to `RAGIndexer` | `src/codex/rag/indexer.py` | `AttributeError: 'RAGIndexer' object has no attribute 'model'` |

**Root cause of the mock failures:** `has_meta_tensors()` checked `hasattr(model, "parameters")` — but `MagicMock` auto-creates all attributes, returning an empty iterator for `.parameters()`. This caused the function to return `False` (no meta tensors) instead of `None` (not an `nn.Module`). `safe_model_to_device` then called `model.to(device)` on the mock, returning `mock.to()` — a chained sub-mock — instead of the original mock. All subsequent `.encode()` / `.get_dimension()` assertions against the original mock object then failed.

---

## ❌ Remaining Failures Requiring Investigation

**25 total failed (pre-fix) → estimated ~13 remaining after S266 fixes.**

Run logs: [Run #738](https://github.com/Aries-Serpent/_codex_/actions/runs/23866089153)

### Group A — `test_retriever_comprehensive.py` (9 failures)

**File:** `tests/rag/test_retriever_comprehensive.py`

#### A1. Network-access failure (1 test)
```
FAILED test_initialization_custom_params
OSError: sentence-transformers/custom-model is not a local folder and is not a
valid model identifier listed on 'https://huggingface.co/models'
```
- **Root cause:** The test passes `model_name="sentence-transformers/custom-model"` which doesn't exist on HuggingFace and requires network access
- **Diagnosis:** The test should mock `safe_load_sentence_transformer` to avoid network calls. CI runners may have HuggingFace blocked.
- **Fix:** Patch `codex.rag._model_utils.safe_load_sentence_transformer` instead of `sentence_transformers.SentenceTransformer` in all retriever tests that load custom models.

#### A2. ImportError not raised (1 test)
```
FAILED test_initialization_model_import_error
Failed: DID NOT RAISE <class 'ImportError'>
```
- **Root cause:** The test expects `ImportError` when `sentence_transformers` is unavailable, but since `sentence_transformers` IS installed in CI, the code never raises it. The test may need to patch the import itself.
- **Fix:** Use `unittest.mock.patch.dict('sys.modules', {'sentence_transformers': None})` to simulate the library being absent.

#### A3. `SentenceTransformer` called 0 times (1 test)
```
FAILED test_initialization_loads_embedding_model
AssertionError: Expected 'SentenceTransformer' to have been called once. Called 0 times.
```
- **Root cause:** `Retriever._load_model()` uses `safe_load_sentence_transformer()` (from `codex.rag._model_utils`), which imports `SentenceTransformer` locally. Patching `codex.rag.retriever.SentenceTransformer` does not intercept the call that goes through `_model_utils`.
- **Fix:** Tests should patch `codex.rag._model_utils.SentenceTransformer` OR patch `codex.rag._model_utils.safe_load_sentence_transformer` directly.

#### A4. `IndexError: index out of range in self` (6 tests)
```
FAILED test_query_basic
FAILED test_query_top_k_respected
FAILED test_query_searches_index
FAILED test_query_adds_timestamp
FAILED test_query_returns_correct_structure
FAILED test_query_handles_invalid_indices
FAILED test_query_with_min_score
FAILED test_query_invalid_top_k
FAILED test_query_encodes_query_text
IndexError: index out of range in self
```
- **Root cause:** The `mock_faiss_index` fixture sets `mock_index.ntotal = 3` and configures `search()` to return specific results, but the FAISS `IndexFlatL2` search call likely isn't being intercepted correctly — `self` in the error refers to the FAISS index object, which is empty (not the mock).
- **Investigation needed:** Check whether `Retriever.faiss_index` is the mock or the real object. The test patches `codex.rag.indexer.load_index`, but verify the patch path is correct. Also verify `Retriever.query()` uses `self.faiss_index` (not a freshly loaded index).

### Group B — `test_indexer_comprehensive.py` (2 failures)

**File:** `tests/rag/test_indexer_comprehensive.py`

```
FAILED test_embed_chunks_basic
FAILED test_embed_chunks_extracts_text_correctly
TypeError: 'NoneType' object is not subscriptable
```
- **Root cause:** Same mock chain issue as `test_embeddings_comprehensive.py` — the `SentenceTransformer` mock is patched at `sentence_transformers.SentenceTransformer` but the code routes through `safe_load_sentence_transformer`. After S266's `has_meta_tensors` fix, these may also be resolved. **Verify after next CI run.**
- If still failing: patch target should be `codex.rag._model_utils.safe_load_sentence_transformer`.

### Group C — `test_rag_integration.py` (2 failures)

**File:** `tests/rag/test_rag_integration.py`

```
FAILED test_batch_embedding_efficiency
AssertionError: assert 0 == 1

FAILED test_embedding_dimension_consistency
AssertionError: assert <MagicMock name='mock.to().get_sentence_embedding_dimension()' id='...'> == (5, 384)
```
- **`test_embedding_dimension_consistency`**: Same `mock.to()` chain issue. After S266's `has_meta_tensors` fix, this may be resolved. **Verify after next CI run.**
- **`test_batch_embedding_efficiency`**: `assert 0 == 1` — the test checks that at least 1 batch encode call was made, but the encoder was called 0 times. Likely same mock chain issue or a different code path than expected.

---

## 🧩 Architectural Issues Identified

1. **Inconsistent mock targets:** All RAG tests patch `sentence_transformers.SentenceTransformer` but the actual loading is done via `codex.rag._model_utils.safe_load_sentence_transformer`. The correct patch target is `codex.rag._model_utils.safe_load_sentence_transformer` (or `codex.rag.embeddings.safe_load_sentence_transformer` etc., depending on where the import is bound). A test utility fixture that patches the correct target would prevent this class of failures.

2. **Network access in tests:** Several tests assume HuggingFace network access (loading `custom-model`, `all-MiniLM-L6-v2`). All RAG tests should be fully offline. Use `@pytest.mark.requires_network` or mock all network calls.

3. **FAISS index mock bypass:** The `IndexError: index out of range in self` errors suggest the FAISS mock isn't being used correctly. Investigate `Retriever.query()` to confirm it reads `self.faiss_index` (set by `_load_index`) and that the patch on `codex.rag.indexer.load_index` is correctly substituting the mock index.

---

## 📁 Affected Files

| File | Role |
|------|------|
| `tests/rag/test_retriever_comprehensive.py` | Fix mock patch targets → `codex.rag._model_utils.safe_load_sentence_transformer` |
| `tests/rag/test_embeddings_comprehensive.py` | Verify fixed after S266; if not, fix mock targets |
| `tests/rag/test_indexer_comprehensive.py` | Verify fixed after S266; if not, fix mock targets |
| `tests/rag/test_rag_integration.py` | Fix mock targets; check `test_batch_embedding_efficiency` call count |
| `src/codex/rag/_model_utils.py` | Central loading function — add `__all__` to expose for targeted patching |
| `src/codex/rag/retriever.py` | `Retriever.query()` — verify FAISS index usage |

---

## 🤖 Agent Continuation Prompt

```
@copilot Continue investigation of RAG Module Tests failures. Context in
`.github/copilot-prompts/active/RAG-test-failures-followup.md`.

**Tasks (in order):**

1. **Verify S266 fixes resolved the mock-chain failures:**
   - Run: `python -m pytest tests/rag/test_embeddings_comprehensive.py tests/rag/test_indexer_comprehensive.py -x -v 2>&1 | tail -30`
   - Expected: All 4 previously failing tests now pass (get_dimension, encode_texts, encode_with_batch_size, encode_with_progress)
   - If still failing: change all `patch('sentence_transformers.SentenceTransformer', ...)` in those files to `patch('codex.rag._model_utils.safe_load_sentence_transformer', return_value=mock_sentence_transformer)`

2. **Fix `test_retriever_comprehensive.py` mock targets:**
   - Replace `patch("codex.rag.retriever.SentenceTransformer", ...)` with `patch("codex.rag._model_utils.safe_load_sentence_transformer", return_value=mock_sentence_transformer)`
   - Fix `test_initialization_model_import_error`: use `patch.dict('sys.modules', {'sentence_transformers': None})` to simulate missing library
   - Fix `test_initialization_custom_params`: mock `safe_load_sentence_transformer` to raise `OSError` for custom model names

3. **Fix IndexError in test_retriever_comprehensive.py query tests:**
   - Add `print(type(retriever.faiss_index))` to a test to confirm mock is wired
   - Verify the patch on `codex.rag.indexer.load_index` is at the correct import path
   - If `Retriever._load_index` imports `load_index` via `from codex.rag.indexer import load_index`, then the correct patch path is `codex.rag.retriever.load_index`

4. **Fix `test_rag_integration.py::test_batch_embedding_efficiency`:**
   - Add debug print to confirm which object `encode` is called on
   - Fix mock target same as items 1-2

5. **Update `.mypy_baseline` if new type errors are introduced.**

6. **Append completion notes to this file under a new ## ✅ Resolution section.**

**Reference commit:** The S266 source-level fixes are in the commit that adds this file.
**Run logs:** https://github.com/Aries-Serpent/_codex_/actions/runs/23866089153
```

---

## ✅ Resolution Log

*(Future agents append findings here)*
