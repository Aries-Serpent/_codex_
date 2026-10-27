"""Exercise emitted guidance as data; never dispatch it or contact a PR."""

from pathlib import Path

import pytest

from scripts.generate_pr_followup import PromptGenerator

ROOT = Path(__file__).resolve().parents[2]
TEMPLATES = ROOT / ".github/copilot-prompts/templates"


@pytest.fixture
def generator(monkeypatch):
    instance = PromptGenerator(TEMPLATES)
    monkeypatch.setattr(
        instance,
        "get_pr_metadata",
        lambda number: {
            "pr_number": number,
            "pr_title": "Fixture only",
            "branch": "fixture",
            "pr_author": "unverified-fixture",
            "date": "2026-10-25",
            "commit_sha": "a" * 40,
            "last_updated": "2026-10-25T00:00:00Z",
        },
    )
    monkeypatch.setattr(instance.git, "get_recent_commits", lambda: [])
    monkeypatch.setattr(instance.git, "get_modified_files", lambda: [])
    monkeypatch.setattr(instance.git, "get_commit_count", lambda: 0)
    return instance


def test_unrelated_pr_cannot_seed_new_candidate(generator, tmp_path):
    previous = tmp_path / "PR-99-followup.md"
    previous.write_text(
        "### Priority 1: Immediate Tasks\n- [ ] Unrelated task\n"
        "**Validation**:\n```bash\nUNRELATED_COMMAND\n```\n"
        "### Priority 2: Follow-Up Validation\n- [ ] Old validation\n"
        "### Priority 3: Future Enhancements\n- [ ] Old future\n---\n"
    )
    output = generator.generate("100", immediate_tasks=["Current task"], output_dir=tmp_path)
    assert "Current task" in output
    assert "Unrelated task" not in output
    assert "UNRELATED_COMMAND" not in output
    assert "sync_tracked_files.py --fix" not in output
    assert previous.read_text().startswith("### Priority 1:")


def test_same_pr_retains_dissent_and_exact_resume_target(generator, tmp_path):
    context = (
        "Candidate a; context x. Dissent: evidence is disputed.\n"
        "Blocked from ANALYZED; pending_requirement=verify-original-F1.\n"
        "Owner proposed, not confirmed; G5 NOT_RUN."
    )
    output = generator.generate(
        "101",
        immediate_tasks=["Bounded task"],
        validation_tasks=["Validate F1"],
        future_tasks=["Later"],
        commands="printf fixture",
        continuation_context=context,
        output_dir=tmp_path,
    )
    generator.save(output, "101", tmp_path)
    regenerated = generator.generate("101", output_dir=tmp_path)
    assert context in regenerated
    for text in ("Bounded task", "Validate F1", "Later", "printf fixture"):
        assert text in regenerated
    assert generator.has_real_content("101", tmp_path)


def test_save_requires_every_preserved_block_not_just_first(generator, tmp_path):
    output = generator.generate(
        "102",
        immediate_tasks=["Keep P1"],
        validation_tasks=["Keep P2"],
        future_tasks=["Keep P3"],
        continuation_context="Dissent and blocked-node evidence",
        output_dir=tmp_path,
    )
    path = generator.save(output, "102", tmp_path)
    before = path.read_bytes()
    generator.save(output.replace("Keep P2", "Dropped"), "102", tmp_path)
    assert path.read_bytes() == before
    generator.save(output.replace("Dissent and blocked-node evidence", "Lost"), "102", tmp_path)
    assert path.read_bytes() == before


@pytest.mark.parametrize(
    "name",
    [
        "pr-continuation",
        "5-pass-self-review",
        "ci-fix-continuation",
        "multi-phase-implementation",
        "consolidation",
    ],
)
def test_actual_emitted_templates_preserve_authority_and_scope(generator, tmp_path, name):
    output = generator.generate("103", template_name=name, output_dir=tmp_path)
    assert "CODEBASE_AGENCY_POLICY.md" in output
    assert "owner/reason" in output
    assert "authorization" in output or "authority" in output
    assert "read-only" in output.lower()
    for forbidden in (
        "Perform mandatory 5-pass",
        "Perform 5 comprehensive",
        "until all checks clear",
        "Execute `@copilot continue",
        "ALL five passes must",
        "gh run rerun",
    ):
        assert forbidden not in output
    assert not list(tmp_path.iterdir())


def test_generation_is_not_dispatch_or_independent_approval(generator, tmp_path):
    output = generator.generate("104", output_dir=tmp_path)
    assert "Self-testing is not independent verification" in output
    assert "do not self-trigger sessions" in output
    assert "read-only tasks permit no edits or dispatch" in output.lower()
    assert "not permission" in output
    assert "Recent commits (not proof of completed tasks)" in output
    assert "No review/approval evidence supplied" in output


@pytest.mark.parametrize("number", ["../105", "0", "-1", "1/2", "x"])
def test_pr_path_components_rejected_before_writes(generator, tmp_path, number):
    with pytest.raises(ValueError, match="PR number"):
        generator.save("data", number, tmp_path)
    assert not list(tmp_path.iterdir())


def test_template_path_traversal_rejected(generator):
    with pytest.raises(ValueError, match="template name"):
        generator.load_template("../active/PR-1-followup")


def test_placeholder_line_does_not_erase_real_findings(generator, tmp_path):
    path = tmp_path / "PR-106-followup.md"
    path.write_text(
        "### Priority 1: Immediate Tasks\n- [ ] No tasks specified\n"
        "- [ ] Preserve disputed finding F1; pending requirement is reproduction\n"
        "### Priority 2: Follow-Up Validation\n- [ ] No tasks specified\n"
        "### Priority 3: Future Enhancements\n- [ ] No tasks specified\n---\n"
    )
    output = generator.generate("106", output_dir=tmp_path)
    assert "Preserve disputed finding F1" in output


def test_explicit_new_context_cannot_erase_preserved_dissent(generator, tmp_path):
    first = generator.generate(
        "107", continuation_context="Disputed F1; resume exact-node-A", output_dir=tmp_path
    )
    generator.save(first, "107", tmp_path)
    output = generator.generate(
        "107", continuation_context="New context without dissent", output_dir=tmp_path
    )
    assert "Disputed F1; resume exact-node-A" in output
    assert "New context without dissent" not in output
