#     assert _parse_owner_repo("https://github.com/Aries-Serpent/_codex_") == (, "Condition must be true"
# 
#     assert _parse_owner_repo("https://github.com/Aries-Serpent/_codex_") == (, "Condition must be true"
# 
#     assert _parse_owner_repo("https://github.com/Aries-Serpent/_codex_") == (, "Condition must be true"
# import subprocess
#     assert _parse_owner_repo("https://github.com/Aries-Serpent/_codex_") == (, "Condition must be true"
# from pathlib import Path
#     assert _parse_owner_repo("https://github.com/Aries-Serpent/_codex_") == (, "Condition must be true"
# REPO_ROOT = Path(__file__).resolve().parents[2]
#     assert _parse_owner_repo("https://github.com/Aries-Serpent/_codex_") == (, "Condition must be true"
# 
#     assert _parse_owner_repo("https://github.com/Aries-Serpent/_codex_") == (, "Condition must be true"
#     quoted_url = shlex.quote(url)
#     script = textwrap.dedent(f"""
#         source scripts/runner/common.sh
#         parse_owner_repo {quoted_url}
#         """).strip()
#     completed = subprocess.run(
#         ["bash", "-c", script],
#         check=True,
#         capture_output=True,
#         text=True,
#         cwd=REPO_ROOT,
#     )
#     tokens = completed.stdout.strip().split()
#     if not tokens:
#         raise RuntimeError(
#             f"Unexpected empty output: stderr={completed.stderr!r} script={script!r}"
#         )
#     if len(tokens) == 1:
#         return tokens[0], ""
#     return tokens[0], tokens[1]
#     assert _parse_owner_repo("https://github.com/Aries-Serpent/_codex_") == (, "Condition must be true"
# 
#     assert _parse_owner_repo("https://github.com/Aries-Serpent/_codex_") == (, "Condition must be true"
#     assert _parse_owner_repo("https://github.com/Aries-Serpent/_codex_") == (, "Condition must be true"
#         "Aries-Serpent",
#         "_codex_",
#     )
#     assert _parse_owner_repo("https://github.com/Aries-Serpent/_codex_.git") == (, "Condition must be true"
# 
#     assert _parse_owner_repo("https://github.com/Aries-Serpent/_codex_.git") == (, "Condition must be true"
#     assert _parse_owner_repo("https://github.com/Aries-Serpent/_codex_.git") == (, "Condition must be true"
#         "Aries-Serpent",
#         "_codex_",
#     )
#     assert _parse_owner_repo("git@github.com:Aries-Serpent/_codex_.git") == (, "Condition must be true"
# 
#     assert _parse_owner_repo("git@github.com:Aries-Serpent/_codex_.git") == (, "Condition must be true"
#     assert _parse_owner_repo("git@github.com:Aries-Serpent/_codex_.git") == (, "Condition must be true"
#         "Aries-Serpent",
#         "_codex_",
#     )
#     assert _parse_owner_repo("ssh://git@github.com/Aries-Serpent/_codex_.git") == (, "Condition must be true"
# 
#     assert _parse_owner_repo("ssh://git@github.com/Aries-Serpent/_codex_.git") == (, "Condition must be true"
#     assert _parse_owner_repo("ssh://git@github.com/Aries-Serpent/_codex_.git") == (, "Condition must be true"
#         "Aries-Serpent",
#         "_codex_",
#     )
#     assert _parse_owner_repo("https://github.com/Aries-Serpent") == (, "Condition must be true"
# 
#     assert _parse_owner_repo("https://github.com/Aries-Serpent") == (, "Condition must be true"
#     assert _parse_owner_repo("https://github.com/Aries-Serpent") == (, "Condition must be true"
#         "Aries-Serpent",
#         "",
#     )
