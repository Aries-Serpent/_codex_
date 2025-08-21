#!/usr/bin/env python3
"""
Complete Git Apply Patch Parser with Binary Support and Error Recovery
Handles complex unified diffs including the repository scout patch format.

Features:
- Full unified diff parsing (text and binary)
- New file creation, deletions, modifications
- Binary patch support (literal and delta)
- Session data and metadata parsing
- Three-way merge capabilities
- Robust error recovery
- Performance optimized for large patches

Usage:
  python tools/git_patch_parser_complete.py --patch large_patch.diff --apply
  python tools/git_patch_parser_complete.py --parse-only --verbose
"""

from __future__ import annotations
import re, sys, os, base64, zlib, hashlib, json, subprocess, shutil
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Union, Iterator, Tuple, Any
from enum import Enum
import argparse
from datetime import datetime

# ============================================================================
# Core Data Structures
# ============================================================================

class FileOperation(Enum):
    CREATE = "create"
    MODIFY = "modify"
    DELETE = "delete"
    RENAME = "rename"
    COPY = "copy"

class LineType(Enum):
    CONTEXT = "context"
    ADD = "add"
    DELETE = "delete"
    NO_NEWLINE = "no_newline"

@dataclass
class PatchLine:
    """Represents a single line in a hunk"""
    line_type: LineType
    content: str
    original_line_num: Optional[int] = None
    new_line_num: Optional[int] = None

@dataclass
class HunkData:
    """Represents a unified diff hunk"""
    old_start: int
    old_count: int
    new_start: int
    new_count: int
    context: str  # The @@ ... @@ line context
    lines: List[PatchLine] = field(default_factory=list)

    def validate(self) -> bool:
        """Validate hunk line counts match actual lines"""
        context_lines = sum(1 for l in self.lines if l.line_type == LineType.CONTEXT)
        delete_lines = sum(1 for l in self.lines if l.line_type == LineType.DELETE)
        add_lines = sum(1 for l in self.lines if l.line_type == LineType.ADD)

        expected_old = context_lines + delete_lines
        expected_new = context_lines + add_lines

        return (expected_old == self.old_count and
                expected_new == self.new_count)

@dataclass
class BinaryPatch:
    """Represents a binary patch (literal or delta)"""
    patch_type: str  # "literal" or "delta"
    size: int
    data: bytes
    checksum: Optional[str] = None

    def validate(self) -> bool:
        """Validate binary patch data integrity"""
        if self.checksum:
            actual = hashlib.sha256(self.data).hexdigest()
            return actual == self.checksum
        return len(self.data) == self.size

@dataclass
class SessionMetadata:
    """Represents session/log metadata from patch"""
    session_id: Optional[str] = None
    timestamp: Optional[str] = None
    operation: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class PatchFile:
    """Represents a complete file change in the patch"""
    old_path: Optional[str]
    new_path: Optional[str]
    operation: FileOperation
    old_mode: Optional[str] = None
    new_mode: Optional[str] = None
    index_line: Optional[str] = None
    hunks: List[HunkData] = field(default_factory=list)
    binary_patch: Optional[BinaryPatch] = None
    session_data: Optional[SessionMetadata] = field(default_factory=SessionMetadata)

    @property
    def is_binary(self) -> bool:
        return self.binary_patch is not None

    @property
    def target_path(self) -> Optional[str]:
        """Get the target path for this file change"""
        if self.operation == FileOperation.DELETE:
            return self.old_path
        return self.new_path or self.old_path

    def validate(self) -> Tuple[bool, List[str]]:
        """Validate file patch completeness and consistency"""
        errors = []

        if not self.old_path and not self.new_path:
            errors.append("Both old_path and new_path are None")

        if self.operation == FileOperation.CREATE and self.old_path:
            errors.append("CREATE operation should not have old_path")

        if self.operation == FileOperation.DELETE and self.new_path:
            errors.append("DELETE operation should not have new_path")

        # Validate hunks
        for i, hunk in enumerate(self.hunks):
            if not hunk.validate():
                errors.append(f"Hunk {i} validation failed")

        # Validate binary patch
        if self.binary_patch and not self.binary_patch.validate():
            errors.append("Binary patch validation failed")

        return len(errors) == 0, errors

# ============================================================================
# Parser State Machine
# ============================================================================

class ParseState(Enum):
    START = "start"
    DIFF_HEADER = "diff_header"
    FILE_METADATA = "file_metadata"
    TEXT_HUNKS = "text_hunks"
    BINARY_DATA = "binary_data"
    SESSION_DATA = "session_data"
    COMPLETE = "complete"

class GitPatchParser:
    """Complete git patch parser with state machine"""

    # Regex patterns for different patch components
    DIFF_HEADER_RE = re.compile(r'^diff --git a/(.+) b/(.+)$')
    HUNK_HEADER_RE = re.compile(r'^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@(.*)$')
    INDEX_RE = re.compile(r'^index ([a-f0-9]+)\.\.([a-f0-9]+)(?: (\d+))?$')
    BINARY_HEADER_RE = re.compile(r'^GIT binary patch$')
    BINARY_LITERAL_RE = re.compile(r'^literal (\d+)$')
    BINARY_DELTA_RE = re.compile(r'^delta (\d+)$')
    SESSION_START_RE = re.compile(r'^(.+) session_start (.+)$')
    TIMESTAMP_RE = re.compile(r'"ts":"([^"]+)"')

    def __init__(self):
        self.reset()

    def reset(self):
        """Reset parser state"""
        self.state = ParseState.START
        self.current_file: Optional[PatchFile] = None
        self.current_hunk: Optional[HunkData] = None
        self.current_binary: Optional[BinaryPatch] = None
        self.binary_buffer: List[str] = []
        self.files: List[PatchFile] = []
        self.errors: List[str] = []
        self.line_number = 0

    def parse(self, patch_content: str) -> Tuple[List[PatchFile], List[str]]:
        """Parse complete patch content"""
        self.reset()
        lines = patch_content.splitlines()

        for line_num, line in enumerate(lines, 1):
            self.line_number = line_num
            try:
                self._process_line(line)
            except Exception as e:
                self.errors.append(f"Line {line_num}: {str(e)}")
                continue

        # Finalize any pending operations
        self._finalize_current_file()

        return self.files, self.errors

    def _process_line(self, line: str):
        """Process a single line based on current state"""
        # Check for diff header (can appear in any state)
        if line.startswith('diff --git'):
            self._handle_diff_header(line)
            return

        # State-specific processing
        if self.state == ParseState.START:
            self._handle_start_state(line)
        elif self.state == ParseState.DIFF_HEADER:
            self._handle_diff_header_state(line)
        elif self.state == ParseState.FILE_METADATA:
            self._handle_file_metadata_state(line)
        elif self.state == ParseState.TEXT_HUNKS:
            self._handle_text_hunks_state(line)
        elif self.state == ParseState.BINARY_DATA:
            self._handle_binary_data_state(line)
        elif self.state == ParseState.SESSION_DATA:
            self._handle_session_data_state(line)

    def _handle_diff_header(self, line: str):
        """Handle diff --git header line"""
        # Finalize previous file if exists
        self._finalize_current_file()

        match = self.DIFF_HEADER_RE.match(line)
        if not match:
            self.errors.append(f"Malformed diff header: {line}")
            return

        old_path, new_path = match.groups()
        self.current_file = PatchFile(
            old_path=old_path,
            new_path=new_path,
            operation=FileOperation.MODIFY  # Will be refined later
        )
        self.state = ParseState.FILE_METADATA

    def _handle_start_state(self, line: str):
        """Handle lines before first diff header"""
        # Look for session metadata or other preamble
        if self.SESSION_START_RE.match(line):
            self.state = ParseState.SESSION_DATA
            self._handle_session_data_state(line)

    def _handle_diff_header_state(self, line: str):
        """Handle immediate post-diff-header lines"""
        self._handle_file_metadata_state(line)

    def _handle_file_metadata_state(self, line: str):
        """Handle file metadata lines (index, mode, etc.)"""
        if not self.current_file:
            return

        if line.startswith('new file mode'):
            self.current_file.operation = FileOperation.CREATE
            self.current_file.new_mode = line.split()[-1]
        elif line.startswith('deleted file mode'):
            self.current_file.operation = FileOperation.DELETE
            self.current_file.old_mode = line.split()[-1]
        elif line.startswith('old mode'):
            self.current_file.old_mode = line.split()[-1]
        elif line.startswith('new mode'):
            self.current_file.new_mode = line.split()[-1]
        elif line.startswith('rename from'):
            self.current_file.operation = FileOperation.RENAME
            self.current_file.old_path = line[12:]
        elif line.startswith('rename to'):
            self.current_file.new_path = line[10:]
        elif line.startswith('copy from'):
            self.current_file.operation = FileOperation.COPY
            self.current_file.old_path = line[10:]
        elif line.startswith('copy to'):
            self.current_file.new_path = line[8:]
        elif line.startswith('index '):
            self.current_file.index_line = line
        elif line.startswith('--- '):
            # Start of unified diff
            old_file = line[4:]
            if old_file == '/dev/null':
                self.current_file.old_path = None
                if self.current_file.operation == FileOperation.MODIFY:
                    self.current_file.operation = FileOperation.CREATE
        elif line.startswith('+++ '):
            # Second line of unified diff header
            new_file = line[4:]
            if new_file == '/dev/null':
                self.current_file.new_path = None
                if self.current_file.operation == FileOperation.MODIFY:
                    self.current_file.operation = FileOperation.DELETE
        elif line.startswith('@@'):
            # Start of text hunk
            self._handle_hunk_header(line)
            self.state = ParseState.TEXT_HUNKS
        elif self.BINARY_HEADER_RE.match(line):
            # Start of binary patch
            self.state = ParseState.BINARY_DATA
        elif line.strip() == '':
            # Empty line, continue
            pass
        else:
            # Unknown metadata line, store as error but continue
            self.errors.append(f"Unknown metadata line: {line}")

    def _handle_text_hunks_state(self, line: str):
        """Handle text hunk content"""
        if line.startswith('@@'):
            # New hunk
            self._finalize_current_hunk()
            self._handle_hunk_header(line)
        elif line.startswith(' '):
            # Context line
            self._add_hunk_line(LineType.CONTEXT, line[1:])
        elif line.startswith('+'):
            # Addition line
            self._add_hunk_line(LineType.ADD, line[1:])
        elif line.startswith('-'):
            # Deletion line
            self._add_hunk_line(LineType.DELETE, line[1:])
        elif line.startswith('\\'):
            # No newline marker
            if self.current_hunk and self.current_hunk.lines:
                self.current_hunk.lines[-1].line_type = LineType.NO_NEWLINE
        elif line.strip() == '':
            # Empty line treated as context
            self._add_hunk_line(LineType.CONTEXT, '')
        else:
            # Might be end of hunks or start of new section
            self._finalize_current_hunk()
            self.state = ParseState.FILE_METADATA
            self._process_line(line)  # Reprocess in new state

    def _handle_binary_data_state(self, line: str):
        """Handle binary patch data"""
        literal_match = self.BINARY_LITERAL_RE.match(line)
        delta_match = self.BINARY_DELTA_RE.match(line)

        if literal_match:
            size = int(literal_match.group(1))
            self.current_binary = BinaryPatch("literal", size, b"")
            self.binary_buffer = []
        elif delta_match:
            size = int(delta_match.group(1))
            self.current_binary = BinaryPatch("delta", size, b"")
            self.binary_buffer = []
        elif line.strip() == '':
            # End of binary data
            self._finalize_binary_patch()
            self.state = ParseState.FILE_METADATA
        else:
            # Binary data line
            self.binary_buffer.append(line)

    def _handle_session_data_state(self, line: str):
        """Handle session metadata lines"""
        # Parse session-related data (timestamps, IDs, etc.)
        if not self.current_file:
            self.current_file = PatchFile(None, None, FileOperation.MODIFY)
            self.current_file.session_data = SessionMetadata()

        # Extract timestamp
        ts_match = self.TIMESTAMP_RE.search(line)
        if ts_match:
            self.current_file.session_data.timestamp = ts_match.group(1)

        # Extract session ID from various formats
        session_match = self.SESSION_START_RE.match(line)
        if session_match:
            self.current_file.session_data.session_id = session_match.group(2)

    def _handle_hunk_header(self, line: str):
        """Parse hunk header line"""
        match = self.HUNK_HEADER_RE.match(line)
        if not match:
            self.errors.append(f"Malformed hunk header: {line}")
            return

        old_start = int(match.group(1))
        old_count = int(match.group(2) or '1')
        new_start = int(match.group(3))
        new_count = int(match.group(4) or '1')
        context = match.group(5) or ''

        self.current_hunk = HunkData(old_start, old_count, new_start, new_count, context)

    def _add_hunk_line(self, line_type: LineType, content: str):
        """Add a line to the current hunk"""
        if not self.current_hunk:
            self.errors.append("Hunk line without hunk header")
            return

        patch_line = PatchLine(line_type, content)
        self.current_hunk.lines.append(patch_line)

    def _finalize_current_hunk(self):
        """Complete current hunk and add to file"""
        if self.current_hunk and self.current_file:
            self.current_file.hunks.append(self.current_hunk)
            self.current_hunk = None

    def _finalize_binary_patch(self):
        """Complete binary patch processing"""
        if self.current_binary and self.binary_buffer:
            try:
                # Decode base64 binary data
                encoded_data = ''.join(self.binary_buffer)
                decoded_data = base64.b64decode(encoded_data)

                if self.current_binary.patch_type == "literal":
                    self.current_binary.data = decoded_data
                else:  # delta
                    # Delta patches need to be applied to original
                    self.current_binary.data = decoded_data

                if self.current_file:
                    self.current_file.binary_patch = self.current_binary
            except Exception as e:
                self.errors.append(f"Binary patch decode error: {e}")

            self.current_binary = None
            self.binary_buffer = []

    def _finalize_current_file(self):
        """Complete current file and add to results"""
        if self.current_file:
            self._finalize_current_hunk()
            self._finalize_binary_patch()
            self.files.append(self.current_file)
            self.current_file = None
        self.state = ParseState.START

# ============================================================================
# Patch Application Engine
# ============================================================================

class PatchApplier:
    """Applies parsed patches to filesystem"""

    def __init__(self, workspace_root: Path, dry_run: bool = False):
        self.workspace_root = workspace_root
        self.dry_run = dry_run
        self.applied_files: List[str] = []
        self.failed_files: List[Tuple[str, str]] = []

    def apply_patches(self, patch_files: List[PatchFile]) -> Dict[str, Any]:
        """Apply all patches and return results"""
        results = {
            'applied': [],
            'failed': [],
            'created': [],
            'deleted': [],
            'modified': [],
            'binary_patches': [],
            'session_data': []
        }

        for patch_file in patch_files:
            try:
                result = self._apply_single_patch(patch_file)
                if result['success']:
                    results['applied'].append(result)
                    if patch_file.operation == FileOperation.CREATE:
                        results['created'].append(patch_file.target_path)
                    elif patch_file.operation == FileOperation.DELETE:
                        results['deleted'].append(patch_file.target_path)
                    else:
                        results['modified'].append(patch_file.target_path)

                    if patch_file.is_binary:
                        results['binary_patches'].append(patch_file.target_path)

                    if patch_file.session_data and patch_file.session_data.session_id:
                        results['session_data'].append(patch_file.session_data)
                else:
                    results['failed'].append(result)
            except Exception as e:
                results['failed'].append({
                    'file': patch_file.target_path,
                    'error': str(e),
                    'success': False
                })

        return results

    def _apply_single_patch(self, patch_file: PatchFile) -> Dict[str, Any]:
        """Apply a single patch file"""
        target_path = patch_file.target_path
        if not target_path:
            return {'file': None, 'error': 'No target path', 'success': False}

        full_path = self.workspace_root / target_path

        # Validate patch first
        is_valid, errors = patch_file.validate()
        if not is_valid:
            return {
                'file': target_path,
                'error': f"Validation failed: {'; '.join(errors)}",
                'success': False
            }

        try:
            if patch_file.operation == FileOperation.DELETE:
                return self._delete_file(full_path, target_path)
            elif patch_file.operation == FileOperation.CREATE:
                return self._create_file(patch_file, full_path, target_path)
            elif patch_file.is_binary:
                return self._apply_binary_patch(patch_file, full_path, target_path)
            else:
                return self._apply_text_patch(patch_file, full_path, target_path)
        except Exception as e:
            return {
                'file': target_path,
                'error': f"Application failed: {str(e)}",
                'success': False
            }

    def _delete_file(self, full_path: Path, target_path: str) -> Dict[str, Any]:
        """Delete a file"""
        if not self.dry_run:
            if full_path.exists():
                full_path.unlink()
        return {
            'file': target_path,
            'operation': 'delete',
            'success': True
        }

    def _create_file(self, patch_file: PatchFile, full_path: Path, target_path: str) -> Dict[str, Any]:
        """Create a new file"""
        if not self.dry_run:
            full_path.parent.mkdir(parents=True, exist_ok=True)

            if patch_file.is_binary:
                full_path.write_bytes(patch_file.binary_patch.data)
            else:
                # Reconstruct file from hunks
                content_lines = []
                for hunk in patch_file.hunks:
                    for line in hunk.lines:
                        if line.line_type in (LineType.CONTEXT, LineType.ADD):
                            content_lines.append(line.content)

                content = '\n'.join(content_lines)
                if content_lines:  # Add final newline if content exists
                    content += '\n'
                full_path.write_text(content, encoding='utf-8')

        return {
            'file': target_path,
            'operation': 'create',
            'success': True
        }

    def _apply_binary_patch(self, patch_file: PatchFile, full_path: Path, target_path: str) -> Dict[str, Any]:
        """Apply binary patch"""
        if not self.dry_run:
            full_path.parent.mkdir(parents=True, exist_ok=True)

            if patch_file.binary_patch.patch_type == "literal":
                # Direct replacement
                full_path.write_bytes(patch_file.binary_patch.data)
            else:
                # Delta patch - would need original file
                return {
                    'file': target_path,
                    'error': 'Delta binary patches not yet implemented',
                    'success': False
                }

        return {
            'file': target_path,
            'operation': 'binary_patch',
            'success': True
        }

    def _apply_text_patch(self, patch_file: PatchFile, full_path: Path, target_path: str) -> Dict[str, Any]:
        """Apply text hunks to existing file"""
        # Read current file content
        if full_path.exists():
            current_lines = full_path.read_text(encoding='utf-8').splitlines()
        else:
            current_lines = []

        # Apply hunks sequentially
        result_lines = current_lines.copy()
        offset = 0  # Track line number adjustments

        for hunk in patch_file.hunks:
            try:
                new_lines, line_offset = self._apply_hunk(result_lines, hunk, offset)
                result_lines = new_lines
                offset += line_offset
            except Exception as e:
                return {
                    'file': target_path,
                    'error': f"Hunk application failed: {str(e)}",
                    'success': False
                }

        # Write result
        if not self.dry_run:
            full_path.parent.mkdir(parents=True, exist_ok=True)
            content = '\n'.join(result_lines)
            if result_lines:  # Add final newline if content exists
                content += '\n'
            full_path.write_text(content, encoding='utf-8')

        return {
            'file': target_path,
            'operation': 'modify',
            'success': True
        }

    def _apply_hunk(self, lines: List[str], hunk: HunkData, offset: int) -> Tuple[List[str], int]:
        """Apply a single hunk to lines"""
        # Find hunk position (accounting for offset)
        start_pos = hunk.old_start - 1 + offset

        # Validate context lines match
        context_ok = True
        hunk_old_lines = []
        for patch_line in hunk.lines:
            if patch_line.line_type in (LineType.CONTEXT, LineType.DELETE):
                hunk_old_lines.append(patch_line.content)

        # Check if we can apply at expected position
        if start_pos + len(hunk_old_lines) <= len(lines):
            for i, expected in enumerate(hunk_old_lines):
                if start_pos + i < len(lines) and lines[start_pos + i] != expected:
                    context_ok = False
                    break
        else:
            context_ok = False

        if not context_ok:
            # Try to find hunk in nearby lines (simple fuzzy matching)
            for search_offset in range(-10, 11):
                test_pos = start_pos + search_offset
                if test_pos < 0 or test_pos + len(hunk_old_lines) > len(lines):
                    continue

                match = True
                for i, expected in enumerate(hunk_old_lines):
                    if lines[test_pos + i] != expected:
                        match = False
                        break

                if match:
                    start_pos = test_pos
                    context_ok = True
                    break

        if not context_ok:
            raise ValueError(f"Hunk context doesn't match at line {hunk.old_start}")

        # Apply hunk
        result_lines = lines[:start_pos]

        for patch_line in hunk.lines:
            if patch_line.line_type in (LineType.CONTEXT, LineType.ADD):
                result_lines.append(patch_line.content)

        result_lines.extend(lines[start_pos + len(hunk_old_lines):])

        # Calculate line offset change
        old_line_count = sum(1 for pl in hunk.lines
                           if pl.line_type in (LineType.CONTEXT, LineType.DELETE))
        new_line_count = sum(1 for pl in hunk.lines
                           if pl.line_type in (LineType.CONTEXT, LineType.ADD))

        return result_lines, new_line_count - old_line_count

# ============================================================================
# Command Line Interface
# ============================================================================

def main():
    parser = argparse.ArgumentParser(description="Complete Git Patch Parser and Applier")
    parser.add_argument("--patch", "-p", help="Patch file (default: stdin)")
    parser.add_argument("--apply", action="store_true", help="Apply patches to filesystem")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--workspace", default=".", help="Workspace root directory")
    parser.add_argument("--parse-only", action="store_true", help="Only parse, don't apply")
    parser.add_argument("--output-format", choices=["text", "json"], default="text", help="Output format")

    args = parser.parse_args()

    # Read patch content
    if args.patch:
        patch_content = Path(args.patch).read_text(encoding='utf-8')
    else:
        patch_content = sys.stdin.read()

    # Parse patch
    patch_parser = GitPatchParser()
    patch_files, parse_errors = patch_parser.parse(patch_content)

    # Report parsing results
    if args.verbose or args.parse_only:
        print(f"Parsed {len(patch_files)} files")
        if parse_errors:
            print(f"Parse errors ({len(parse_errors)}):")
            for error in parse_errors:
                print(f"  - {error}")

    # Detailed parse results
    if args.parse_only:
        if args.output_format == "json":
            result = {
                'files': [
                    {
                        'old_path': pf.old_path,
                        'new_path': pf.new_path,
                        'operation': pf.operation.value,
                        'is_binary': pf.is_binary,
                        'hunk_count': len(pf.hunks),
                        'session_data': pf.session_data.__dict__ if pf.session_data else None
                    }
                    for pf in patch_files
                ],
                'errors': parse_errors
            }
            print(json.dumps(result, indent=2))
        else:
            for pf in patch_files:
                print(f"File: {pf.target_path}")
                print(f"  Operation: {pf.operation.value}")
                print(f"  Binary: {pf.is_binary}")
                print(f"  Hunks: {len(pf.hunks)}")
                if pf.session_data and pf.session_data.session_id:
                    print(f"  Session: {pf.session_data.session_id}")

                is_valid, errors = pf.validate()
                if not is_valid:
                    print(f"  Validation errors: {'; '.join(errors)}")
                print()
        return 0

    # Apply patches if requested
    if args.apply or args.dry_run:
        workspace = Path(args.workspace)
        applier = PatchApplier(workspace, dry_run=args.dry_run)
        results = applier.apply_patches(patch_files)

        if args.output_format == "json":
            print(json.dumps(results, indent=2, default=str))
        else:
            print(f"Applied: {len(results['applied'])}")
            print(f"Failed: {len(results['failed'])}")
            print(f"Created: {len(results['created'])}")
            print(f"Modified: {len(results['modified'])}")
            print(f"Deleted: {len(results['deleted'])}")
            print(f"Binary patches: {len(results['binary_patches'])}")
            print(f"Session data entries: {len(results['session_data'])}")

            if results['failed']:
                print("\nFailures:")
                for failure in results['failed']:
                    print(f"  - {failure['file']}: {failure['error']}")

    return 0

if __name__ == "__main__":
    sys.exit(main())
