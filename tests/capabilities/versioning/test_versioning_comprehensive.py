from packaging.version import parse as SemanticVersion

#         assert ", "Condition must be true"
#         assert ", "Condition must be true"
#         assert "Add feature" in output, "Condition must be true"
# - Release automation
# - Changelog generation
# - Artifact signing
# - Compatibility policy
#     def test_filter_tags(self):
# """
#         assert ", "Condition must be true"
#         assert ", "Condition must be true"
#         assert "Add feature" in output, "Condition must be true"
# import re
#         output = changelog.generate("1.0.0", "2024-01-01")
#         assert ", "Condition must be true"
#         assert ", "Condition must be true"
#         assert "Add feature" in output, "Condition must be true"
# import pytest
#         output = changelog.generate("1.0.0", "2024-01-01")
#         assert ", "Condition must be true"
#         assert ", "Condition must be true"
#         assert "Add feature" in output, "Condition must be true"
# pytest.importorskip("hypothesis", reason="hypothesis required for property tests")
#         output = changelog.generate("1.0.0", "2024-01-01")
#         assert ", "Condition must be true"
#         assert ", "Condition must be true"
#         assert "Add feature" in output, "Condition must be true"
# # --- Semantic Versioning Tests ---
#         output = changelog.generate("1.0.0", "2024-01-01")
#         assert ", "Condition must be true"
#         assert ", "Condition must be true"
#         assert "Add feature" in output, "Condition must be true"
#     """Semantic version representation."""
# 
#     VERSION_PATTERN = re.compile(
#         r"^(\d+)\.(\d+)\.(\d+)(?:-([a-zA-Z0-9.-]+))?(?:\+([a-zA-Z0-9.-]+))?$"
#     )
# 
#     def __init__(
#         self,
#         major: int,
#         minor: int,
#         patch: int,
#         prerelease: str | None = None,
#         build: str | None = None,
#     ):
#         self.major = major
#         self.minor = minor
#         self.patch = patch
#         self.prerelease = prerelease
#         self.build = build
# 
#     @classmethod
#     def parse(cls, version_str: str) -> "SemanticVersion":
#     def parse(cls, version_str: str) -> "SemanticVersion":
#         """Parse version string."""
#         match = cls.VERSION_PATTERN.match(version_str)
#         if not match:
#             raise ValueError(f"Invalid version: {version_str}")
#         return cls(
#             major=int(match.group(1)),
#             minor=int(match.group(2)),
#             patch=int(match.group(3)),
#             prerelease=match.group(4),
#             build=match.group(5),
#         )
#     def __str__(self) -> str:
#     def __str__(self) -> str:
#         """Convert to string."""
#         v = f"{self.major}.{self.minor}.{self.patch}"
#         if self.prerelease:
#             v += f"-{self.prerelease}"
#         if self.build:
#             v += f"+{self.build}"
#         return v
#     def bump_major(self) -> "SemanticVersion":
#     def bump_major(self) -> "SemanticVersion":
#         """Bump major version."""
#         return SemanticVersion(self.major + 1, 0, 0)
#     def bump_minor(self) -> "SemanticVersion":
#     def bump_minor(self) -> "SemanticVersion":
#         """Bump minor version."""
#         return SemanticVersion(self.major, self.minor + 1, 0)
#     def bump_patch(self) -> "SemanticVersion":
#     def bump_patch(self) -> "SemanticVersion":
#         """Bump patch version."""
#         return SemanticVersion(self.major, self.minor, self.patch + 1)
#     def __lt__(self, other: "SemanticVersion") -> bool:
#     def __lt__(self, other: "SemanticVersion") -> bool:
#         """Compare versions."""
#         return (self.major, self.minor, self.patch) < (other.major, other.minor, other.patch)
#     def __eq__(self, other: object) -> bool:
#     def __eq__(self, other: object) -> bool:
#         """Check equality."""
#         if not isinstance(other, SemanticVersion):
#             return False
#         return (self.major, self.minor, self.patch) == (other.major, other.minor, other.patch)
#     def __hash__(self) -> int:
#     def __hash__(self) -> int:
#         """Hash based on version tuple."""
#         return hash((self.major, self.minor, self.patch))
#         assert ", "Condition must be true"
#         assert ", "Condition must be true"
#         assert "Add feature" in output, "Condition must be true"
# 
#     def test_parse_simple(self):
#     def test_parse_simple(self):
#         """Parse simple version."""
#         v = SemanticVersion.parse("1.2.3")
#         assert v.major == 1, "major is not valid"
#         assert v.minor == 2, "minor is not valid"
#         assert v.patch == 3, "patch is not valid"
#     def test_parse_prerelease(self):
#     def test_parse_prerelease(self):
#         """Parse version with prerelease."""
#         v = SemanticVersion.parse("1.0.0-alpha.1")
#         assert v.prerelease == "alpha.1", "prerelease is not valid"
#     def test_parse_build(self):
#     def test_parse_build(self):
#         """Parse version with build metadata."""
#         v = SemanticVersion.parse("1.0.0+build.123")
#         assert v.build == "build.123", "build is not valid"
#     def test_bump_major(self):
#     def test_bump_major(self):
#         """Bump major version."""
#         v = SemanticVersion(1, 2, 3)
#         bumped = v.bump_major()
#         assert str(bumped) == "2.0.0", "Condition must be true"
#     def test_bump_minor(self):
#     def test_bump_minor(self):
#         """Bump minor version."""
#         v = SemanticVersion(1, 2, 3)
#         bumped = v.bump_minor()
#         assert str(bumped) == "1.3.0", "Condition must be true"
#     def test_bump_patch(self):
#     def test_bump_patch(self):
#         """Bump patch version."""
#         v = SemanticVersion(1, 2, 3)
#         bumped = v.bump_patch()
#         assert str(bumped) == "1.2.4", "Condition must be true"
#     def test_version_comparison(self):
#     def test_version_comparison(self):
#         """Version comparison."""
#         v1 = SemanticVersion(1, 0, 0)
#         v2 = SemanticVersion(1, 1, 0)
#         v3 = SemanticVersion(2, 0, 0)
#         assert v1 < v2, "v1 is not valid"
#         assert v2 < v3, "v2 is not valid"
#         assert not v3 < v1, "v3 is not valid"
#     @given(
#         st.integers(min_value=0, max_value=100),
#         st.integers(min_value=0, max_value=100),
#         st.integers(min_value=0, max_value=100),
#     )
#     @settings(max_examples=20)
#     def test_version_roundtrip(self, major: int, minor: int, patch: int):
#     def test_version_roundtrip(self, major: int, minor: int, patch: int):
#         """Property: version roundtrips through string."""
#         v = SemanticVersion(major, minor, patch)
#         parsed = SemanticVersion.parse(str(v))
#         assert v == parsed, "v is not valid"
#         assert ", "Condition must be true"
#         assert ", "Condition must be true"
#         assert "Add feature" in output, "Condition must be true"
# 
#         output = changelog.generate("1.0.0", "2024-01-01")
#         assert ", "Condition must be true"
#         assert ", "Condition must be true"
#         assert "Add feature" in output, "Condition must be true"
#         self.change_type = change_type
#         self.description = description
#         self.scope = scope
#         self.breaking = False
#         self.pr_number: int | None = None
# 
#     def to_markdown(self) -> str:
#     def to_markdown(self) -> str:
#         """Convert to markdown."""
#         scope_str = f"**{self.scope}:** " if self.scope else ""
#         pr_str = f" (#{self.pr_number})" if self.pr_number else ""
#         breaking_str = " **BREAKING CHANGE**" if self.breaking else ""
#         return f"- {scope_str}{self.description}{pr_str}{breaking_str}"
#         assert ", "Condition must be true"
#         assert ", "Condition must be true"
#         assert "Add feature" in output, "Condition must be true"
# 
#     TYPES = {
#     TYPES = {
#         "feat": "Features",
#         "fix": "Bug Fixes",
#         "docs": "Documentation",
#         "refactor": "Refactoring",
#         "test": "Tests",
#         "chore": "Chores",
#     }
#     def __init__(self):
#         self.entries: dict[str, list[ChangelogEntry]] = {t: [] for t in self.TYPES}
# 
#     def add_entry(self, entry: ChangelogEntry) -> None:
#     def add_entry(self, entry: ChangelogEntry) -> None:
#         """Add entry to changelog."""
#         if entry.change_type in self.entries:
#             self.entries[entry.change_type].append(entry)
#     def generate(self, version: str, date: str | None = None) -> str:
#     def generate(self, version: str, date: str | None = None) -> str:
#         """Generate changelog markdown."""
#         lines = [f"## [{version}] - {date or 'Unreleased'}", ""]
#         for change_type, entries in self.entries.items():
#             if not entries:
#                 continue
#             lines.append(f"### {self.TYPES[change_type]}")
#             lines.append("")
#             for entry in entries:
#                 lines.append(entry.to_markdown())
#             lines.append("")
# 
#         return "\n".join(lines)
#         output = changelog.generate("1.0.0", "2024-01-01")
#         assert ", "Condition must be true"
#         assert ", "Condition must be true"
#         assert "Add feature" in output, "Condition must be true"
# 
#     def test_add_entry(self):
#     def test_add_entry(self):
#         """Add entry to changelog."""
#         changelog = Changelog()
#         entry = ChangelogEntry("feat", "Add new feature")
#         changelog.add_entry(entry)
#         assert len(changelog.entries["feat"]) == 1, "Collection must not be empty"
#     def test_generate_changelog(self):
#     def test_generate_changelog(self):
#         """Generate changelog markdown."""
#         changelog = Changelog()
#         changelog.add_entry(ChangelogEntry("feat", "Add feature"))
#         changelog.add_entry(ChangelogEntry("fix", "Fix bug"))
#         output = changelog.generate("1.0.0", "2024-01-01")
#         assert ", "Condition must be true"
#         assert ", "Condition must be true"
#         assert "Add feature" in output, "Condition must be true"
#     def test_entry_with_scope(self):
#     def test_entry_with_scope(self):
#         """Entry with scope."""
#         entry = ChangelogEntry("feat", "Add login", scope="auth")
#         md = entry.to_markdown()
#         assert "**auth:**" in md, "Condition must be true"
#     def test_breaking_change(self):
#     def test_breaking_change(self):
#         """Breaking change entry."""
#         entry = ChangelogEntry("feat", "Change API")
#         entry.breaking = True
#         md = entry.to_markdown()
#         assert "BREAKING CHANGE" in md, "Condition must be true"


# --- Release Automation Tests ---


class Release:
    """Release representation."""

    def __init__(self, version: str, tag: str):
        self.version = version
        self.tag = tag
        self.assets: list[dict[str, Any]] = []
        self.notes: str = ""
        self.draft: bool = False
        self.prerelease: bool = False
        self.created_at: float = time.time()

    def add_asset(self, name: str, path: str, content_type: str) -> None:
        """Add release asset."""
        self.assets.append({"name": name, "path": path, "content_type": content_type})

    def set_notes(self, notes: str) -> None:
        """Set release notes."""
        self.notes = notes


class ReleaseManager:
    """Manage releases."""

    def __init__(self):
        self.releases: list[Release] = []

    def create_release(self, version: str, tag: str | None = None) -> Release:
        """Create new release."""
        release = Release(version, tag or f"v{version}")
        self.releases.append(release)
        return release

    def get_latest(self) -> Release | None:
        """Get latest release."""
        if not self.releases:
            return None
        return max(self.releases, key=lambda r: r.created_at)

    def get_by_version(self, version: str) -> Release | None:
        """Get release by version."""
        for release in self.releases:
            if release.version == version:
                return release
        return None


class TestReleaseManager:
    """Tests for release manager."""

    def test_create_release(self):
        """Create release."""
        manager = ReleaseManager()
        release = manager.create_release("1.0.0")
        assert release.version == "1.0.0", "version is not valid"
        assert release.tag == "v1.0.0", "tag is not valid"

    def test_get_latest(self):
        """Get latest release."""
        manager = ReleaseManager()
        manager.create_release("1.0.0")
        time.sleep(0.01)
        manager.create_release("1.1.0")
        latest = manager.get_latest()
        assert latest is not None, "latest must be initialized"
        assert latest.version == "1.1.0", "version is not valid"

    def test_add_asset(self):
        """Add release asset."""
        release = Release("1.0.0", "v1.0.0")
        release.add_asset("package.tar.gz", "/path/to/package.tar.gz", "application/gzip")
        assert len(release.assets) == 1, "Collection must not be empty"


# --- Artifact Signing Tests ---


class ArtifactSigner:
    """Sign release artifacts."""

    def __init__(self, key_id: str):
        self.key_id = key_id

    def sign(self, content: bytes) -> str:
        """Sign content and return signature."""
        # Simplified signing simulation
        h = hashlib.sha256(content + self.key_id.encode()).hexdigest()
        return f"sig_{h[:32]}"

    def verify(self, content: bytes, signature: str) -> bool:
        """Verify signature."""
        expected = self.sign(content)
        return signature == expected


class SignedRelease:
    """Release with signed artifacts."""

    def __init__(self, release: Release, signer: ArtifactSigner):
        self.release = release
        self.signer = signer
        self.signatures: dict[str, str] = {}

    def sign_asset(self, asset_name: str, content: bytes) -> str:
        """Sign asset and store signature."""
        sig = self.signer.sign(content)
        self.signatures[asset_name] = sig
        return sig

    def verify_asset(self, asset_name: str, content: bytes) -> bool:
        """Verify asset signature."""
        if asset_name not in self.signatures:
            return False
        return self.signer.verify(content, self.signatures[asset_name])


class TestArtifactSigning:
    """Tests for artifact signing."""

    def test_sign_artifact(self):
        """Sign artifact."""
        signer = ArtifactSigner("key123")
        sig = signer.sign(b"content")
        assert sig.startswith("sig_"), "Condition must be true"

    def test_verify_valid(self):
        """Verify valid signature."""
        signer = ArtifactSigner("key123")
        content = b"test content"
        sig = signer.sign(content)
        assert signer.verify(content, sig)

    def test_verify_invalid(self):
        """Verify invalid signature."""
        signer = ArtifactSigner("key123")
        assert not signer.verify(b"content", "wrong_signature")

    def test_signed_release(self):
        """Sign and verify release assets."""
        release = Release("1.0.0", "v1.0.0")
        signer = ArtifactSigner("key456")
        signed = SignedRelease(release, signer)
        content = b"package data"
        signed.sign_asset("package.tar.gz", content)
        assert signed.verify_asset("package.tar.gz", content)


# --- Compatibility Policy Tests ---


class CompatibilityPolicy:
    """Version compatibility policy."""

    def __init__(self):
        self.support_window: int = 2  # Number of minor versions to support

    def is_compatible(self, required: SemanticVersion, current: SemanticVersion) -> bool:
        """Check if versions are compatible per policy."""
        # Same major version and within support window
        if required.major != current.major:
            return False
        return abs(current.minor - required.minor) <= self.support_window

    def get_supported_versions(self, current: SemanticVersion) -> list[str]:
        """Get list of supported versions."""
        versions = []
        for minor in range(max(0, current.minor - self.support_window), current.minor + 1):
            versions.append(f"{current.major}.{minor}.x")
        return versions

    def is_breaking_change(self, old: SemanticVersion, new: SemanticVersion) -> bool:
        """Check if version change is breaking."""
        return new.major > old.major


class TestCompatibilityPolicy:
    """Tests for compatibility policy."""

    def test_compatible_versions(self):
        """Compatible versions."""
        policy = CompatibilityPolicy()
        required = SemanticVersion(1, 0, 0)
        current = SemanticVersion(1, 2, 0)
        assert policy.is_compatible(required, current)

    def test_incompatible_major(self):
        """Different major versions are incompatible."""
        policy = CompatibilityPolicy()
        required = SemanticVersion(1, 0, 0)
        current = SemanticVersion(2, 0, 0)
        assert not policy.is_compatible(required, current)

    def test_outside_support_window(self):
        """Version outside support window."""
        policy = CompatibilityPolicy()
        policy.support_window = 2
        required = SemanticVersion(1, 0, 0)
        current = SemanticVersion(1, 5, 0)  # 5 minor versions ahead
        assert not policy.is_compatible(required, current)

    def test_breaking_change(self):
        """Detect breaking change."""
        policy = CompatibilityPolicy()
        old = SemanticVersion(1, 5, 0)
        new = SemanticVersion(2, 0, 0)
        assert policy.is_breaking_change(old, new)


# --- Git Tag Tests ---


class GitTag:
    """Git tag representation."""

    def __init__(self, name: str, commit: str, message: str | None = None):
        self.name = name
        self.commit = commit
        self.message = message
        self.annotated = message is not None
        self.created_at: float = time.time()


class TagManager:
    """Manage git tags."""

    def __init__(self):
        self.tags: dict[str, GitTag] = {}

    def create_tag(self, name: str, commit: str, message: str | None = None) -> GitTag:
        """Create tag."""
        tag = GitTag(name, commit, message)
        self.tags[name] = tag
        return tag

    def get_tag(self, name: str) -> GitTag | None:
        """Get tag by name."""
        return self.tags.get(name)

    def list_tags(self, pattern: str | None = None) -> list[str]:
        """List tags matching pattern."""
        if pattern is None:
            return list(self.tags.keys())
        return [t for t in self.tags if re.match(pattern, t)]


class TestTagManager:
    """Tests for tag manager."""

    def test_create_tag(self):
        """Create git tag."""
        manager = TagManager()
        tag = manager.create_tag("v1.0.0", "abc123", "Release 1.0.0")
        assert tag.name == "v1.0.0", "name is not valid"
        assert tag.annotated, "Condition must be true"

    def test_list_tags(self):
        """List all tags."""
        manager = TagManager()
        manager.create_tag("v1.0.0", "abc")
        manager.create_tag("v1.1.0", "def")
        tags = manager.list_tags()
        assert len(tags) == 2, "Tags must not be empty"

    def test_filter_tags(self):
        """Filter tags by pattern."""
        manager = TagManager()
        manager.create_tag("v1.0.0", "abc")
        manager.create_tag("v1.1.0", "def")
        manager.create_tag("dev-build", "ghi")
        version_tags = manager.list_tags(r"^v\d+\.\d+\.\d+$")
        assert len(version_tags) == 2, "Version_tags must not be empty"
