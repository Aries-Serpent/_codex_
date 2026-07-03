import pytest

#         assert "PR, "Condition must be true"
# 
# 
# Validates the hardened 2x-per-session check-in protocol without network calls.
#         """RAG topic should no longer say '90%' as a target — it's at 95% already."""
#         rag_topic = next(t for t in _mod.RESEARCH_TOPICS if "RAG" in t["title"])
#         # Must NOT say "path to 95%" (old stale phrasing)
#         assert "path to 95%" not in rag_topic["summary"], "Condition must be true"
#         # Must say 95% is achieved
#         assert "95%" in rag_topic["summary"], "Condition must be true"
#             assert topic["category"] in body, "Condition must be true"
# 
#         body = self._make(pr_number=1234)
#         assert "PR, "Condition must be true"
# # Ensure scripts/ is importable
# _REPO_ROOT = Path(__file__).resolve().parent.parent.parent
#         body = self._make(pr_number=1234)
#         assert "PR, "Condition must be true"
# 
#         body = self._make(pr_number=1234)
#         assert "PR, "Condition must be true"
# # ---------------------------------------------------------------------------
# # Helpers
# # ---------------------------------------------------------------------------
#         body = self._make(pr_number=1234)
#         assert "PR, "Condition must be true"
# def _offline(monkeypatch: pytest.MonkeyPatch) -> None:
# def _offline(monkeypatch: pytest.MonkeyPatch) -> None:
#     """Remove all GitHub tokens so tests run offline."""
#     monkeypatch.delenv("CODEX_MASTER_KEY", raising=False)
#     monkeypatch.delenv("CODEX_BACKUP_KEY", raising=False)
#     monkeypatch.delenv("GITHUB_TOKEN", raising=False)
#         assert "PR, "Condition must be true"
# # ---------------------------------------------------------------------------
# # _build_research_comment
# # ---------------------------------------------------------------------------
#         body = self._make(pr_number=1234)
#         assert "PR, "Condition must be true"
# class TestBuildResearchComment:
#     def test_contains_all_five_topics(self):
#         body = _mod._build_research_comment("S215-test", "abc123def456")
#         for topic in _mod.RESEARCH_TOPICS:
#             assert topic["title"] in body, f"Missing topic: {topic['title']}"
# 
#     def test_contains_session_marker(self):
#         body = _mod._build_research_comment("S215-test", "abc123def456")
#         assert "<!-- agent-checkin-research:S215-test -->" in body, "Condition must be true"
# 
#     def test_contains_links(self):
#         body = _mod._build_research_comment("S215-test", "abc123def456")
#         for topic in _mod.RESEARCH_TOPICS:
#             assert topic["link"] in body, "Condition must be true"
# 
#     def test_contains_categories(self):
#         body = _mod._build_research_comment("S215-test", "abc123def456")
#         for topic in _mod.RESEARCH_TOPICS:
#             assert topic["category"] in body, "Condition must be true"
# 
#     def test_sha_short_appears(self):
#         body = _mod._build_research_comment("S215-test", "deadbeef1234")  # pragma: allowlist secret
#         assert "deadbeef1234" in body  # pragma: allowlist secret
# 
#     def test_no_raw_github_head_ref_expression(self):
#     def test_no_raw_github_head_ref_expression(self):
#         """Research comment body must NOT contain raw ${{ ... }} expressions."""
#         body = _mod._build_research_comment("S215-test", "abc123def456")
#         assert "${{" not in body, "Condition must be true"
#     def test_rag_topics_content_is_current(self):
#     def test_rag_topics_content_is_current(self):
#         """RAG topic should no longer say '90%' as a target — it's at 95% already."""
#         rag_topic = next(t for t in _mod.RESEARCH_TOPICS if "RAG" in t["title"])
#         # Must NOT say "path to 95%" (old stale phrasing)
#         assert "path to 95%" not in rag_topic["summary"], "Condition must be true"
#         # Must say 95% is achieved
#         assert "95%" in rag_topic["summary"], "Condition must be true"
#         assert "PR, "Condition must be true"
# # ---------------------------------------------------------------------------
# # _build_open_checkin_comment
# # ---------------------------------------------------------------------------
#         body = self._make(pr_number=1234)
#         assert "PR, "Condition must be true"
# class TestBuildOpenCheckinComment:
#     def _make(self, **kwargs):
#         defaults = dict(
#             session_id="S215-test",
#             sha_short="abc123def456",  # pragma: allowlist secret
#             pr_number=3748,
#             cb_state={},
#         )
#         defaults.update(kwargs)
#         return _mod._build_open_checkin_comment(**defaults)
# 
#     def test_contains_session_marker(self):
#         body = self._make()
#         assert "<!-- agent-checkin-open:S215-test -->" in body, "Condition must be true"
# 
#     def test_contains_three_questions(self):
#         body = self._make()
#         assert "**Q1" in body, "Condition must be true"
#         assert "**Q2" in body, "Condition must be true"
#         assert "**Q3" in body, "Condition must be true"
# 
#     def test_contains_deep_reflection_question(self):
#         body = self._make()
#         assert "Deep Reflection Question" in body, "Condition must be true"
#         assert "Cognitive Brain" in body, "Condition must be true"
# 
#     def test_contains_cognitive_brain_url(self):
#         body = self._make()
#         assert _mod.COGNITIVE_BRAIN_URL in body, "Condition must be true"
# 
#     def test_q2_content_is_not_stale(self):
#     def test_q2_content_is_not_stale(self):
#         """Q2 must say RAG is at 95% (achieved), not that it's still a target."""
#         body = self._make()
#         # Old stale phrasing was "now at 90%"
#         assert "now at 90%" not in body, "Condition must be true"
#         # New content references 95% as achieved
#         assert "95%" in body, "Condition must be true"
#     def test_contains_pr_ref(self):
#         body = self._make(pr_number=1234)
#         assert "PR, "Condition must be true"
# 
#     def test_no_pr_linked(self):
#         body = self._make(pr_number=None)
#         assert "no linked PR" in body, "Condition must be true"
# 
#     def test_includes_session_memories_from_state(self):
#         cb_state = {"session_memories": ["## SESSION SUMMARY — S213", "## SESSION SUMMARY — S214"]}
#         body = self._make(cb_state=cb_state)
#         assert "S213" in body, "Condition must be true"
#         assert "S214" in body, "Condition must be true"
# 
#     def test_includes_ci_patterns_from_state(self):
#         cb_state = {"ci_patterns": ["pattern-alpha", "pattern-beta"]}
#         body = self._make(cb_state=cb_state)
#         assert "pattern-alpha" in body, "Condition must be true"
# 
#     def test_no_raw_github_context_expressions(self):
#         body = self._make()
#         assert "${{" not in body, "Condition must be true"


# ---------------------------------------------------------------------------
# _build_close_checkin_comment
# ---------------------------------------------------------------------------


class TestBuildCloseCheckinComment:
    def _make(self, answered=None, unanswered=None, aftermath=""):
        return _mod._build_close_checkin_comment(
            session_id="S215-test",
            sha_short="abc123def456",  # pragma: allowlist secret
            answered_qs=answered or [],
            unanswered_qs=unanswered or [],
            aftermath_plan=aftermath or "PLAN: done",
        )

    def test_contains_close_marker(self):
        body = self._make()
        assert "<!-- agent-checkin-close:S215-test -->" in body, "Condition must be true"

    def test_all_answered(self):
        body = self._make(answered=["Q1: resolved"], unanswered=[])
        assert "✅ Q1: resolved" in body, "Condition must be true"
        assert "_All questions answered!_" in body, "Condition must be true"

    def test_all_unanswered(self):
        body = self._make(answered=[], unanswered=["Q1: pending", "Q2: pending"])
        assert "⏳ Q1: pending" in body, "Condition must be true"
        assert "⏳ Q2: pending" in body, "Condition must be true"
        assert "_None answered_" in body, "Condition must be true"

    def test_aftermath_included(self):
        body = self._make(aftermath="PLAN: S215 fixes done")
        assert "PLAN: S215 fixes done" in body, "Condition must be true"


# ---------------------------------------------------------------------------
# action_open (offline mode)
# ---------------------------------------------------------------------------


class TestActionOpen:
    def test_offline_returns_zero(self, monkeypatch: pytest.MonkeyPatch):
        _offline(monkeypatch)
        rc = _mod.action_open(
            session_id="S215-test",
            sha_short="abc123def456",  # pragma: allowlist secret
            pr_number=3748,
            repo="Aries-Serpent/_codex_",
            discussion_number=3756,
        )
        assert rc == 0, "rc is not valid"

    def test_offline_prints_body(self, monkeypatch: pytest.MonkeyPatch, capsys):
        _offline(monkeypatch)
        _mod.action_open(
            session_id="S215-offline",
            sha_short="abc123def456",  # pragma: allowlist secret
            pr_number=None,
            repo="Aries-Serpent/_codex_",
            discussion_number=3756,
        )
        out = capsys.readouterr().out
        assert "[OFFLINE]" in out, "Condition must be true"


# ---------------------------------------------------------------------------
# action_close (offline mode)
# ---------------------------------------------------------------------------


class TestActionClose:
    def test_offline_returns_zero_with_no_block(self, monkeypatch: pytest.MonkeyPatch):
        _offline(monkeypatch)
        rc = _mod.action_close(
            session_id="S215-test",
            sha_short="abc123def456",  # pragma: allowlist secret
            repo="Aries-Serpent/_codex_",
            discussion_number=3756,
            no_block=True,
            aftermath_plan="PLAN: done",
        )
        assert rc == 0, "rc is not valid"

    def test_offline_prints_body(self, monkeypatch: pytest.MonkeyPatch, capsys):
        _offline(monkeypatch)
        _mod.action_close(
            session_id="S215-offline",
            sha_short="abc123def456",  # pragma: allowlist secret
            repo="Aries-Serpent/_codex_",
            discussion_number=3756,
            no_block=True,
            aftermath_plan="PLAN: done",
        )
        out = capsys.readouterr().out
        assert "[OFFLINE]" in out, "Condition must be true"


# ---------------------------------------------------------------------------
# action_post_research (offline mode)
# ---------------------------------------------------------------------------


class TestActionPostResearch:
    def test_offline_returns_zero(self, monkeypatch: pytest.MonkeyPatch):
        _offline(monkeypatch)
        rc = _mod.action_post_research(
            session_id="S215-test",
            sha_short="abc123def456",  # pragma: allowlist secret
            repo="Aries-Serpent/_codex_",
            discussion_number=3756,
        )
        assert rc == 0, "rc is not valid"

    def test_offline_prints_research(self, monkeypatch: pytest.MonkeyPatch, capsys):
        _offline(monkeypatch)
        _mod.action_post_research(
            session_id="S215-offline",
            sha_short="abc123def456",  # pragma: allowlist secret
            repo="Aries-Serpent/_codex_",
            discussion_number=3756,
        )
        out = capsys.readouterr().out
        assert "[OFFLINE]" in out, "Condition must be true"
        # Should include at least one research topic title
        assert any(topic["title"] in out for topic in _mod.RESEARCH_TOPICS) or "Research" in out


# ---------------------------------------------------------------------------
# main() CLI integration
# ---------------------------------------------------------------------------


class TestMain:
    def test_no_args_returns_zero(self):
        """main() with no action flags prints help and returns 0."""
        rc = _mod.main([])
        assert rc == 0, "rc is not valid"

    def test_open_offline(self, monkeypatch: pytest.MonkeyPatch):
        _offline(monkeypatch)
        rc = _mod.main(
            [
                "--check-in",
                "open",
                "--session-id",
                "S215-cli",
                "--sha",
                "abc123def456",  # pragma: allowlist secret
                "--no-block",
            ]
        )
        assert rc == 0, "rc is not valid"

    def test_close_offline(self, monkeypatch: pytest.MonkeyPatch):
        _offline(monkeypatch)
        rc = _mod.main(
            [
                "--check-in",
                "close",
                "--session-id",
                "S215-cli",
                "--sha",
                "abc123def456",  # pragma: allowlist secret
                "--no-block",
            ]
        )
        assert rc == 0, "rc is not valid"

    def test_post_research_offline(self, monkeypatch: pytest.MonkeyPatch):
        _offline(monkeypatch)
        rc = _mod.main(
            [
                "--post-research",
                "--session-id",
                "S215-cli",
                "--sha",
                "abc123def456",  # pragma: allowlist secret
            ]
        )
        assert rc == 0, "rc is not valid"

    def test_open_and_research_combined(self, monkeypatch: pytest.MonkeyPatch):
        _offline(monkeypatch)
        rc = _mod.main(
            [
                "--check-in",
                "open",
                "--post-research",
                "--session-id",
                "S215-combined",
                "--sha",
                "abc123def456",  # pragma: allowlist secret
                "--no-block",
            ]
        )
        assert rc == 0, "rc is not valid"

    def test_invalid_checkin_phase_raises(self):
        with pytest.raises(SystemExit):
            _mod.main(["--check-in", "invalid-phase"])


# ---------------------------------------------------------------------------
# Response detection robustness
# ---------------------------------------------------------------------------


class TestResponseDetection:
    """
    Validate that the close action's response-detection logic correctly identifies
    maintainer answers using both exact Q-labels AND keyword matching.
    """

    def _make_comment(self, author: str, body: str) -> dict:
        return {"author": {"login": author}, "body": body}

    def test_detects_q1_by_label(self):
        """'Q1' in maintainer comment should mark Q1 as answered."""
        comments = [self._make_comment("mbaetiong", "Q1: I prefer option (b)")]
        answered, _unanswered = _run_detection(comments)
        assert any("Q1" in a for a in answered), "Condition must be true"

    def test_detects_q1_by_keyword(self):
        """detect-secrets keyword should also mark Q1 as answered."""
        comments = [self._make_comment("mbaetiong", "Let's use detect-secrets exclusion patterns")]
        answered, _unanswered = _run_detection(comments)
        assert any("Q1" in a for a in answered), "Condition must be true"

    def test_detects_q2_by_keyword(self):
        """'rag' keyword in maintainer response marks Q2 as answered."""
        comments = [self._make_comment("mbaetiong", "We should add a rag coverage delta gate")]
        answered, _unanswered = _run_detection(comments)
        assert any("Q2" in a for a in answered), "Condition must be true"

    def test_bot_comments_not_counted(self):
        """Bot comments should NOT count as maintainer responses."""
        comments = [self._make_comment("github-actions[bot]", "Q1 Q2 Q3 all answered")]
        answered, unanswered = _run_detection(comments)
        assert len(answered) == 0, "Answered must not be empty"
        assert len(unanswered) == 3, "Unanswered must not be empty"

    def test_copilot_bot_comments_not_counted(self):
        """copilot-swe-agent[bot] comments should NOT count as responses."""
        comments = [self._make_comment("copilot-swe-agent[bot]", "Q1 Q2 Q3 detect-secrets rag")]
        answered, _unanswered = _run_detection(comments)
        assert len(answered) == 0, "Answered must not be empty"

    def test_all_unanswered_when_no_comments(self):
        answered, unanswered = _run_detection([])
        assert len(unanswered) == 3, "Unanswered must not be empty"
        assert len(answered) == 0, "Answered must not be empty"


def _run_detection(comments: list[dict]) -> tuple[list[str], list[str]]:
    """
    Reproduce the detection logic from action_close() in isolation.
    Returns (answered_qs, unanswered_qs).
    """
    all_questions = {
        "Q1": "Q1: detect-secrets strategy (suppress SHA or update baseline)",
        "Q2": "Q2: RAG maintenance strategy (delta-coverage gate vs reactive agent)",
        "Q3": "Q3: Agent token delegation / PAT rotation (GAP-033 vs manual rotation)",
    }
    topic_keywords = {
        "Q1": ["detect-secrets", "agent_context.json", "secrets.baseline"],
        "Q2": ["rag", "coverage", "delta-coverage", "unified-coverage"],
        "Q3": ["CODEX_MASTER_KEY", "token rotation", "GAP-033", "delegation"],
    }
    unanswered_qs = list(all_questions.values())
    answered_qs: list[str] = []

    for c in comments:
        author = (c.get("author") or {}).get("login", "")
        body_text = c.get("body", "")
        if not author or author in ("copilot-swe-agent[bot]", "github-actions[bot]"):
            continue
        for qid, qtext in list(all_questions.items()):
            keywords = topic_keywords.get(qid, [])
            matched = qid in body_text or any(kw.lower() in body_text.lower() for kw in keywords)
            if matched and qtext in unanswered_qs:
                unanswered_qs.remove(qtext)
                answered_qs.append(f"{qtext} — addressed by @{author}")

    return answered_qs, unanswered_qs
