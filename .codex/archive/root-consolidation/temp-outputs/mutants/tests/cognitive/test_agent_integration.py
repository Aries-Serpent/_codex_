#         assert ", "Condition must be true"
#         assert "test-agent" in section, "Condition must be true"
# Tests the agent integration registry, core agent integration,
#     def test_is_integrated_extended_agent(self) -> None:
# extended agent integration, and brain integration section generation.
#         """Test is_integrated for extended agents."""
#         with tempfile.TemporaryDirectory() as tmpdir:
#             manifest_path = Path(tmpdir) / "manifest.json"
#             integrate_extended_agents(manifest_path)
#             registry = AgentIntegrationRegistry(manifest_path)
#             assert registry.is_integrated("documentation-consolidator"), "Condition must be true"
#             assert registry.is_integrated("rag-index-manager"), "Condition must be true"
#             assert registry.is_integrated("repository-hygiene-agent"), "Condition must be true"
#             assert not registry.is_integrated("unknown-agent"), "Condition must be true"
