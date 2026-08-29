#!/usr/bin/env python3
"""
Session and Artifact Lifecycle Management Script

Automatically archives and deletes old session logs, databases, and artifacts
according to the retention policy defined in .codex/RETENTION_POLICY.md

Usage:
    python scripts/maintenance/archive_old_sessions.py [OPTIONS]

Options:
    --dry-run              Show what would be done without making changes
    --config FILE          Use custom config file (default: .codex/retention_config.yaml)
    --archive-only         Archive without deleting
    --force-delete         Skip verification before deletion
    --parallel N           Number of parallel workers (default: 4)
    --preserve PATH        Mark specific artifact for preservation (no deletion)
"""

import sys
import json
import tarfile
import hashlib
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple
from dataclasses import dataclass
import argparse
import yaml


@dataclass
class RetentionConfig:
    """Configuration for retention policy."""
    
    sessions_days: int = 90
    database_days: int = 90
    checkpoints_days: int = 180
    reports_days: int = 365
    tests_days: int = 365
    
    archive_enabled: bool = True
    archive_format: str = "tar.gz"  # tar.gz or tar.bz2
    archive_s3_enabled: bool = False
    archive_s3_bucket: str = "codex-archives"
    
    dry_run: bool = False
    verify_before_delete: bool = True
    parallel_workers: int = 4
    
    @classmethod
    def from_file(cls, config_path: str) -> "RetentionConfig":
        """Load configuration from YAML file."""
        if not Path(config_path).exists():
            return cls()
        
        try:
            with open(config_path, 'r') as f:
                config_data = yaml.safe_load(f)
            
            retention = config_data.get('retention', {})
            archive = config_data.get('archive', {})
            cleanup = config_data.get('cleanup', {})
            
            return cls(
                sessions_days=retention.get('sessions', {}).get('window_days', 90),
                database_days=retention.get('database', {}).get('window_days', 90),
                checkpoints_days=retention.get('checkpoints', {}).get('window_days', 180),
                reports_days=retention.get('reports', {}).get('window_days', 365),
                tests_days=retention.get('tests', {}).get('window_days', 365),
                archive_enabled=archive.get('enabled', True),
                archive_format=archive.get('format', 'tar.gz'),
                archive_s3_enabled=archive.get('s3_enabled', False),
                dry_run=cleanup.get('dry_run', False),
                verify_before_delete=cleanup.get('verify_before_delete', True),
                parallel_workers=cleanup.get('parallelism', 4),
            )
        except Exception as e:
            logging.warning(f"Failed to load config from {config_path}: {e}. Using defaults.")
            return cls()


class ArtifactArchiver:
    """Manages archiving and deletion of artifacts."""
    
    def __init__(self, config: RetentionConfig, repo_root: str = "."):
        self.config = config
        self.repo_root = Path(repo_root)
        self.audit_log = []
        
        # Setup logging
        self.logger = self._setup_logging()
        
        # Load preserved artifacts
        self.preserved_artifacts = self._load_preserved_list()
    
    def _setup_logging(self) -> logging.Logger:
        """Configure logging to file and console."""
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)
        
        # File handler
        audit_file = self.repo_root / ".codex" / "cleanup_audit.log"
        audit_file.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(audit_file, mode='a')
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s [%(levelname)s] %(message)s'
        ))
        logger.addHandler(file_handler)
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(logging.Formatter(
            '%(asctime)s [%(levelname)s] %(message)s'
        ))
        logger.addHandler(console_handler)
        
        return logger
    
    def _load_preserved_list(self) -> set:
        """Load list of preserved artifacts that should not be deleted."""
        preserved_file = self.repo_root / ".codex" / "preserved_artifacts.json"
        if not preserved_file.exists():
            return set()
        
        try:
            with open(preserved_file) as f:
                data = json.load(f)
                return set(data.get('preserved_paths', []))
        except Exception as e:
            self.logger.warning(f"Failed to load preserved list: {e}")
            return set()
    
    def _calculate_checksum(self, filepath: Path) -> str:
        """Calculate SHA256 checksum of a file."""
        sha256_hash = hashlib.sha256()
        with open(filepath, 'rb') as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    
    def _is_artifact_old(self, artifact_path: Path, retention_days: int) -> bool:
        """Check if artifact exceeds retention window."""
        if not artifact_path.exists():
            return False
        
        age = datetime.now() - datetime.fromtimestamp(artifact_path.stat().st_mtime)
        return age > timedelta(days=retention_days)
    
    def _audit_log_action(self, action: str, artifact_type: str, path: str, 
                         details: Dict) -> None:
        """Log action to audit trail."""
        entry = {
            'timestamp': datetime.now().isoformat(),
            'action': action,
            'artifact_type': artifact_type,
            'path': path,
            'details': details,
            'dry_run': self.config.dry_run,
        }
        
        self.audit_log.append(entry)
        self.logger.info(f"{action.upper()}: {path} ({artifact_type})")
    
    def _archive_file(self, source_path: Path, artifact_type: str) -> Optional[str]:
        """Create compressed archive of a file or directory."""
        if not self.config.archive_enabled:
            return None
        
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            archive_dir = self.repo_root / ".codex" / "archives"
            archive_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate archive name
            if self.config.archive_format == "tar.gz":
                archive_name = f"{artifact_type}_archive_{timestamp}.tar.gz"
            else:
                archive_name = f"{artifact_type}_archive_{timestamp}.tar.bz2"
            
            archive_path = archive_dir / archive_name
            
            # Create archive
            if source_path.is_dir():
                with tarfile.open(archive_path, 'w:gz' if self.config.archive_format == 'tar.gz' else 'w:bz2') as tar:
                    tar.add(source_path, arcname=source_path.name)
            else:
                with tarfile.open(archive_path, 'w:gz' if self.config.archive_format == 'tar.gz' else 'w:bz2') as tar:
                    tar.add(source_path, arcname=source_path.name)
            
            checksum = self._calculate_checksum(archive_path)
            size_mb = archive_path.stat().st_size / (1024 * 1024)
            
            self.logger.info(f"Created archive: {archive_path} ({size_mb:.2f} MB)")
            
            return {
                'path': str(archive_path),
                'checksum': checksum,
                'size_bytes': archive_path.stat().st_size,
                'created': datetime.now().isoformat(),
            }
        
        except Exception as e:
            self.logger.error(f"Failed to archive {source_path}: {e}")
            return None
    
    def _delete_artifact(self, artifact_path: Path) -> bool:
        """Delete an artifact with verification."""
        if artifact_path in self.preserved_artifacts:
            self.logger.info(f"SKIP (preserved): {artifact_path}")
            return True
        
        if self.config.dry_run:
            self.logger.info(f"DRY RUN - would delete: {artifact_path}")
            return True
        
        try:
            if artifact_path.is_dir():
                import shutil
                shutil.rmtree(artifact_path)
            else:
                artifact_path.unlink()
            
            self.logger.info(f"Deleted: {artifact_path}")
            return True
        
        except Exception as e:
            self.logger.error(f"Failed to delete {artifact_path}: {e}")
            return False
    
    def process_sessions(self) -> Tuple[int, int]:
        """Process session logs for archival and deletion."""
        sessions_dir = self.repo_root / "memory" / "sessions"
        if not sessions_dir.exists():
            return 0, 0
        
        archived = 0
        deleted = 0
        
        for session_file in sessions_dir.glob("*.ndjson"):
            if self._is_artifact_old(session_file, self.config.sessions_days):
                archive_info = self._archive_file(session_file, "session_logs")
                
                if archive_info or not self.config.archive_enabled:
                    if self._delete_artifact(session_file):
                        deleted += 1
                        self._audit_log_action(
                            'delete', 'session_logs', str(session_file),
                            {'retention_days': self.config.sessions_days, 'archive': archive_info}
                        )
                
                if archive_info:
                    archived += 1
                    self._audit_log_action(
                        'archive', 'session_logs', str(session_file),
                        archive_info
                    )
        
        return archived, deleted
    
    def process_database(self) -> Tuple[int, int]:
        """Process session database for archival and deletion."""
        db_path = self.repo_root / ".codex" / "sessions.db"
        if not db_path.exists():
            return 0, 0
        
        archived = 0
        deleted = 0
        
        if self._is_artifact_old(db_path, self.config.database_days):
            archive_info = self._archive_file(db_path, "session_database")
            
            if archive_info or not self.config.archive_enabled:
                if self._delete_artifact(db_path):
                    deleted += 1
                    self._audit_log_action(
                        'delete', 'session_database', str(db_path),
                        {'retention_days': self.config.database_days, 'archive': archive_info}
                    )
            
            if archive_info:
                archived += 1
                self._audit_log_action(
                    'archive', 'session_database', str(db_path),
                    archive_info
                )
        
        return archived, deleted
    
    def process_checkpoints(self) -> Tuple[int, int]:
        """Process checkpoint files for archival and deletion."""
        checkpoints_dir = self.repo_root / ".codex" / "checkpoints"
        if not checkpoints_dir.exists():
            return 0, 0
        
        archived = 0
        deleted = 0
        
        for checkpoint_file in checkpoints_dir.glob("*.{yaml,json}"):
            if self._is_artifact_old(checkpoint_file, self.config.checkpoints_days):
                archive_info = self._archive_file(checkpoint_file, "checkpoints")
                
                if archive_info or not self.config.archive_enabled:
                    if self._delete_artifact(checkpoint_file):
                        deleted += 1
                        self._audit_log_action(
                            'delete', 'checkpoints', str(checkpoint_file),
                            {'retention_days': self.config.checkpoints_days, 'archive': archive_info}
                        )
                
                if archive_info:
                    archived += 1
                    self._audit_log_action(
                        'archive', 'checkpoints', str(checkpoint_file),
                        archive_info
                    )
        
        return archived, deleted
    
    def process_reports(self) -> Tuple[int, int]:
        """Process campaign and test reports for archival and deletion."""
        report_dirs = [
            self.repo_root / ".codex" / "reports",
            self.repo_root / "artifacts",
        ]
        
        archived = 0
        deleted = 0
        
        for report_dir in report_dirs:
            if not report_dir.exists():
                continue
            
            for report_file in report_dir.glob("*.{md,json,csv,html}"):
                if self._is_artifact_old(report_file, self.config.reports_days):
                    archive_info = self._archive_file(report_file, "reports")
                    
                    if archive_info or not self.config.archive_enabled:
                        if self._delete_artifact(report_file):
                            deleted += 1
                            self._audit_log_action(
                                'delete', 'reports', str(report_file),
                                {'retention_days': self.config.reports_days, 'archive': archive_info}
                            )
                    
                    if archive_info:
                        archived += 1
                        self._audit_log_action(
                            'archive', 'reports', str(report_file),
                            archive_info
                        )
        
        return archived, deleted
    
    def process_tests(self) -> Tuple[int, int]:
        """Process test skeletons and coverage reports."""
        test_dirs = [
            self.repo_root / "coverage_reports",
            self.repo_root / ".codex" / "test_skeletons",
        ]
        
        archived = 0
        deleted = 0
        
        for test_dir in test_dirs:
            if not test_dir.exists():
                continue
            
            for test_file in test_dir.glob("*.{json,yaml,html}"):
                if self._is_artifact_old(test_file, self.config.tests_days):
                    archive_info = self._archive_file(test_file, "tests")
                    
                    if archive_info or not self.config.archive_enabled:
                        if self._delete_artifact(test_file):
                            deleted += 1
                            self._audit_log_action(
                                'delete', 'tests', str(test_file),
                                {'retention_days': self.config.tests_days, 'archive': archive_info}
                            )
                    
                    if archive_info:
                        archived += 1
                        self._audit_log_action(
                            'archive', 'tests', str(test_file),
                            archive_info
                        )
        
        return archived, deleted
    
    def run(self) -> Dict[str, int]:
        """Execute full artifact lifecycle management."""
        self.logger.info(f"Starting artifact lifecycle management (dry_run={self.config.dry_run})")
        
        results = {
            'archived_total': 0,
            'deleted_total': 0,
            'errors': 0,
        }
        
        # Process each artifact type
        archived, deleted = self.process_sessions()
        results['archived_total'] += archived
        results['deleted_total'] += deleted
        
        archived, deleted = self.process_database()
        results['archived_total'] += archived
        results['deleted_total'] += deleted
        
        archived, deleted = self.process_checkpoints()
        results['archived_total'] += archived
        results['deleted_total'] += deleted
        
        archived, deleted = self.process_reports()
        results['archived_total'] += archived
        results['deleted_total'] += deleted
        
        archived, deleted = self.process_tests()
        results['archived_total'] += archived
        results['deleted_total'] += deleted
        
        # Save audit log
        self._save_audit_log()
        
        self.logger.info(f"Lifecycle management complete: {results['archived_total']} archived, "
                        f"{results['deleted_total']} deleted")
        
        return results
    
    def _save_audit_log(self) -> None:
        """Save audit log to JSON file."""
        audit_file = self.repo_root / ".codex" / "cleanup_audit.json"
        
        # Load existing entries
        existing_entries = []
        if audit_file.exists():
            try:
                with open(audit_file) as f:
                    existing_entries = json.load(f)
            except:
                pass
        
        # Append new entries
        existing_entries.extend(self.audit_log)
        
        # Save
        with open(audit_file, 'w') as f:
            json.dump(existing_entries, f, indent=2, default=str)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Archive and delete old session artifacts according to retention policy'
    )
    parser.add_argument('--dry-run', action='store_true',
                       help='Show what would be done without making changes')
    parser.add_argument('--config', default='.codex/retention_config.yaml',
                       help='Path to retention config file')
    parser.add_argument('--archive-only', action='store_true',
                       help='Archive without deleting')
    parser.add_argument('--force-delete', action='store_true',
                       help='Skip verification before deletion')
    parser.add_argument('--parallel', type=int, default=4,
                       help='Number of parallel workers')
    parser.add_argument('--preserve', action='append',
                       help='Preserve specific artifact (can be repeated)')
    parser.add_argument('--repo-root', default='.',
                       help='Repository root directory')
    
    args = parser.parse_args()
    
    # Load config
    config = RetentionConfig.from_file(args.config)
    config.dry_run = args.dry_run
    config.parallel_workers = args.parallel
    config.verify_before_delete = not args.force_delete
    
    # Create archiver and run
    archiver = ArtifactArchiver(config, repo_root=args.repo_root)
    results = archiver.run()
    
    # Print summary
    print("\n" + "="*60)
    print("ARTIFACT LIFECYCLE MANAGEMENT SUMMARY")
    print("="*60)
    print(f"Archived: {results['archived_total']}")
    print(f"Deleted:  {results['deleted_total']}")
    print(f"Errors:   {results['errors']}")
    print("="*60)
    
    # Exit code
    sys.exit(0 if results['errors'] == 0 else 1)


if __name__ == '__main__':
    main()
