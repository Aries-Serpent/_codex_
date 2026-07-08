#         assert result["contents"][0]["text"].startswith(", "Result must not be empty"


class TestCompletionHandlers:
    """Tests for completion-related handlers."""

    def test_completion_complete_handler(self):
        """completion/complete returns completions."""

        def handle_completion(params):
            ref = params.get("ref", {})
            argument = params.get("argument", {})

            ref_type = ref.get("type")
            arg_name = argument.get("name")
            arg_value = argument.get("value", "")

            # Mock completions
            completions = {
                ("ref/prompt", "text"): ["Hello", "Hi there", "Greetings"],
                ("ref/resource", "uri"): ["file:///a.txt", "file:///b.txt"],
            }

            key = (ref_type, arg_name)
            values = completions.get(key, [])

            # Filter by prefix
            filtered = [v for v in values if v.lower().startswith(arg_value.lower())]

            return {"completion": {"values": filtered, "hasMore": False}}

        result = handle_completion(
            {"ref": {"type": "ref/prompt"}, "argument": {"name": "text", "value": "H"}}
        )

        assert "completion" in result, "Result must not be empty"
        assert len(result["completion"]["values"]) == 2, "Collection must not be empty"


class TestNotificationHandlers:
    """Tests for notification handlers."""

    def test_progress_notification(self):
        """Progress notifications are handled."""
        progress_updates = []

        def handle_progress(params):
            token = params.get("progressToken")
            progress = params.get("progress")
            total = params.get("total")

            progress_updates.append({"token": token, "progress": progress, "total": total})

        handle_progress({"progressToken": "op-1", "progress": 50, "total": 100})

        assert len(progress_updates) == 1, "Progress_updates must not be empty"
        assert progress_updates[0]["progress"] == 50, "Condition must be true"

    def test_cancelled_notification(self):
        """Cancelled notifications stop operations."""
        cancelled_ops = set()

        def handle_cancelled(params):
            request_id = params.get("requestId")
            cancelled_ops.add(request_id)

        handle_cancelled({"requestId": "req-1"})

        assert "req-1" in cancelled_ops, "Condition must be true"

    def test_initialized_notification(self):
        """Initialized notification completes handshake."""
        state = {"initialized": False}

        def handle_initialized(params):
            state["initialized"] = True

        handle_initialized({})

        assert state["initialized"] is True, "Condition must be true"
