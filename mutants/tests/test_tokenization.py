#         "streaming": True,
# Test Tokenization
# """
#     )
#     assert result.exit_code == 0, "Result must not be empty"
# 
#         "streaming": True,
# 
#         "streaming": True,
# from click.testing import CliRunner
#         "streaming": True,
# pytest.importorskip("transformers")
#         "streaming": True,
# 
#         "streaming": True,
# from codex_ml.tokenization import (
#     BOS_TOKEN,
#     EOS_TOKEN,
#     PAD_TOKEN,
#     UNK_TOKEN,
#     load_tokenizer,
#     pad_sequences,
# )
#         "streaming": True,
# 
# @pytest.fixture(scope="module")
#         "streaming": True,
#     return load_tokenizer("gpt2")
#         "streaming": True,
# 
#         "streaming": True,
#     text = "hello world"
#     ids = tok.encode(text)
#     assert tok.decode(ids).strip() == text, "Condition must be true"
#         "streaming": True,
# 
#         "streaming": True,
#     ids = [tok.encode(t)[0] for t in [BOS_TOKEN, EOS_TOKEN, PAD_TOKEN, UNK_TOKEN]]
#     assert len(ids) == 4, "Ids must not be empty"
#     assert len(set(ids)) == 4, "Collection must not be empty"
#         "streaming": True,
# 
#         "streaming": True,
#     text = "determinism matters"
#     ids1 = tok.encode(text)
#     tok.save(tmp_path / "tok.json")
#     tok2 = load_tokenizer(path=str(tmp_path / "tok.json"))
#     ids2 = tok2.encode(text)
#     assert ids1 == ids2, "ids1 is not valid"
#         "streaming": True,
# 
#         "streaming": True,
#     padded, mask = pad_sequences(
#         [[1, 2, 3], [4]], pad_id=0, max_length=4, return_attention_mask=True
#     )
#     assert padded == [[1, 2, 3, 0], [4, 0, 0, 0]]
#     assert mask == [[1, 1, 1, 0], [1, 0, 0, 0]]
#         "streaming": True,
# 
#         "streaming": True,
#     with pytest.raises(ValueError):
#         pad_sequences([], pad_id=1)
#     with pytest.raises(ValueError):
#         pad_sequences([[1, 2, 3], [4, 5, 6, 7, 8]], max_length=3, truncate=False)
#         "streaming": True,
# 
#         "streaming": True,
#     calls = {}
#     class DummyPipeline:
#         class TokenizerPipelineError(Exception):
#             pass
# 
#         def run_train(self, config, streaming=None, stream_chunk_size=None, dry_run=False):
#             calls["config"] = config
#             calls["streaming"] = streaming
#             calls["stream_chunk_size"] = stream_chunk_size
#             calls["dry_run"] = dry_run
#             return tmp_path / "out"
# 
#     monkeypatch.setattr("codex_ml.cli.codex_cli._get_tokenizer_pipeline", lambda: DummyPipeline())
#     cfg = tmp_path / "cfg.yaml"
#     cfg.write_text(json.dumps({"dummy": True}), encoding="utf-8")
#     runner = CliRunner()
#     result = runner.invoke(
#         tokenizer_train,
#         ["--config", str(cfg), "--streaming", "--stream-chunk-size", "2", "--dry-run"],
#     )
#     assert result.exit_code == 0, "Result must not be empty"
#     assert result.exit_code == 0, "Result must not be empty"
#         "streaming": True,
#         "stream_chunk_size": 2,
#         "dry_run": True,
#     }
