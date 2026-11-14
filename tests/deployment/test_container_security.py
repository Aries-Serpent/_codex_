"""
Test Container Security

Test module for container security.
"""

from pathlib import Path

# The root Dockerfile moved to .config/ in 7a37ae201b (rename, content
# unchanged); container-scan.yml scans this same path.
DOCKERFILE = Path(__file__).resolve().parents[2] / ".config" / "Dockerfile"


def test_no_root_user_in_container() -> None:
    dockerfile = DOCKERFILE.read_text(encoding="utf-8")
    assert "USER appuser" in dockerfile, "Condition must be true"

    # Every runnable (terminal) stage must finish as a non-root user. Stages
    # used only as a parent (``FROM base AS cpu-runtime``) may build as root;
    # the effective USER is inherited, so walk the parent chain.
    stages: dict[str, dict[str, str | None]] = {}
    order: list[str] = []
    for raw in dockerfile.splitlines():
        line = raw.strip()
        if line.upper().startswith("FROM "):
            parts = line.split()
            image = parts[1]
            name = parts[3] if len(parts) >= 4 and parts[2].upper() == "AS" else f"#{len(order)}"
            stages[name] = {"parent": image if image in stages else None, "user": None}
            order.append(name)
        elif line.upper().startswith("USER ") and order:
            stages[order[-1]]["user"] = line.split(None, 1)[1].strip()
    assert order, "Dockerfile must define at least one stage"
    parents = {s["parent"] for s in stages.values() if s["parent"]}
    terminal = [n for n in order if n not in parents]
    assert terminal, "Dockerfile must have a runnable stage"
    for name in terminal:
        user, cur = None, name
        while cur is not None and user is None:
            user, cur = stages[cur]["user"], stages[cur]["parent"]
        assert user is not None, f"stage {name!r} runs as root (no USER)"
        assert user.split(":")[0] not in {"root", "0"}, f"stage {name!r} ends as root"


def test_minimal_attack_surface() -> None:
    dockerfile = DOCKERFILE.read_text(encoding="utf-8")
    assert "apt-get" in dockerfile, "Condition must be true"
    assert "curl" in dockerfile, "Condition must be true"
