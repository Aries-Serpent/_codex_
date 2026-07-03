"""
MCP Tool Mock Generators

Provides mock response generators for 12 MCP tools for testing and development.

Authority: Lane 3 Unified Documentation Agent
Status: Task 3.3 Implementation
"""

import random
from typing import Dict, List, Any
from datetime import datetime, timedelta
import uuid


class MockDataGenerator:
    """Base class for mock data generation"""
    
    @staticmethod
    def random_id(prefix: str = "") -> str:
        """Generate random ID"""
        return f"{prefix}{uuid.uuid4().hex[:8]}"
    
    @staticmethod
    def random_sha() -> str:
        """Generate random git SHA"""
        return uuid.uuid4().hex[:40]
    
    @staticmethod
    def random_iso_date(days_ago: int = 0) -> str:
        """Generate random ISO date"""
        dt = datetime.now() - timedelta(days=days_ago)
        return dt.isoformat() + "Z"
    
    @staticmethod
    def random_email() -> str:
        """Generate random email"""
        names = ["alice", "bob", "charlie", "diana", "eve"]
        domains = ["example.com", "test.org", "demo.io"]
        return f"{random.choice(names)}@{random.choice(domains)}"


# ==============================================================================
# 1. SEARCH CODE MOCK
# ==============================================================================

class SearchCodeMockGenerator(MockDataGenerator):
    """Mock generator for search_code tool"""
    
    @staticmethod
    def generate_result() -> Dict[str, Any]:
        """Generate single code search result"""
        languages = ["python", "javascript", "go", "rust", "java"]
        repos = ["codex", "aries-serpent", "platform", "core", "sdk"]
        
        return {
            "path": f"src/{random.choice(repos)}/module_{random.randint(1, 10)}.py",
            "repository": f"org/{random.choice(repos)}",
            "ref": "refs/heads/main",
            "matches": random.randint(1, 5),
            "text_matches": [
                {
                    "object_url": "https://api.github.com/repos/org/repo/code-search/1",
                    "object_type": "CodeSearchResultItem",
                    "property": "content",
                    "fragment": "def authenticate(username, password):\n    return oauth.validate(username, password)",
                    "matches": [{"text": "def authenticate", "indices": [0, 15]}]
                }
            ]
        }
    
    @staticmethod
    def generate_response(query: str, results: int = 10) -> Dict[str, Any]:
        """Generate search_code response"""
        return {
            "total_count": random.randint(100, 5000),
            "incomplete_results": False,
            "items": [SearchCodeMockGenerator.generate_result() for _ in range(results)]
        }


# ==============================================================================
# 2. SEARCH ISSUES MOCK
# ==============================================================================

class SearchIssuesMockGenerator(MockDataGenerator):
    """Mock generator for search_issues tool"""
    
    @staticmethod
    def generate_issue() -> Dict[str, Any]:
        """Generate single issue"""
        states = ["open", "closed"]
        labels = ["bug", "feature", "documentation", "enhancement"]
        
        return {
            "id": random.randint(1000000, 9999999),
            "number": random.randint(1, 500),
            "title": f"Issue: {random.choice(['Fix', 'Add', 'Improve', 'Refactor'])} {random.choice(['authentication', 'error handling', 'performance', 'documentation'])}",
            "body": "This is a sample issue description with details about the problem.",
            "state": random.choice(states),
            "labels": [{"name": l} for l in random.sample(labels, k=random.randint(1, 2))],
            "user": {
                "login": random.choice(["alice", "bob", "charlie"]),
                "id": random.randint(1000, 9999),
            },
            "created_at": SearchIssuesMockGenerator.random_iso_date(days_ago=random.randint(0, 30)),
            "updated_at": SearchIssuesMockGenerator.random_iso_date(days_ago=random.randint(0, 10)),
            "repository_url": "https://api.github.com/repos/org/repo",
            "score": round(random.uniform(1.0, 100.0), 2),
        }
    
    @staticmethod
    def generate_response(query: str, results: int = 10) -> Dict[str, Any]:
        """Generate search_issues response"""
        return {
            "total_count": random.randint(10, 1000),
            "incomplete_results": False,
            "items": [SearchIssuesMockGenerator.generate_issue() for _ in range(results)]
        }


# ==============================================================================
# 3. SEARCH PULL REQUESTS MOCK
# ==============================================================================

class SearchPRsMockGenerator(MockDataGenerator):
    """Mock generator for search_pull_requests tool"""
    
    @staticmethod
    def generate_pr() -> Dict[str, Any]:
        """Generate single PR"""
        return {
            "id": random.randint(1000000, 9999999),
            "number": random.randint(100, 5000),
            "title": f"PR: {random.choice(['Add', 'Fix', 'Improve'])} {random.choice(['docs', 'tests', 'core', 'API'])}",
            "body": "This PR includes improvements to the codebase...",
            "state": random.choice(["open", "closed"]),
            "head": {
                "label": f"user:feature-{random.randint(1, 100)}",
                "sha": SearchPRsMockGenerator.random_sha(),
            },
            "base": {
                "label": "main",
                "sha": SearchPRsMockGenerator.random_sha(),
            },
            "user": {
                "login": random.choice(["alice", "bob", "charlie"]),
                "id": random.randint(1000, 9999),
            },
            "created_at": SearchPRsMockGenerator.random_iso_date(days_ago=random.randint(0, 30)),
            "updated_at": SearchPRsMockGenerator.random_iso_date(days_ago=random.randint(0, 10)),
            "draft": random.choice([True, False]),
            "score": round(random.uniform(1.0, 100.0), 2),
        }
    
    @staticmethod
    def generate_response(query: str, results: int = 10) -> Dict[str, Any]:
        """Generate search_pull_requests response"""
        return {
            "total_count": random.randint(10, 500),
            "incomplete_results": False,
            "items": [SearchPRsMockGenerator.generate_pr() for _ in range(results)]
        }


# ==============================================================================
# 4. GET FILE CONTENTS MOCK
# ==============================================================================

class GetFileContentsMockGenerator(MockDataGenerator):
    """Mock generator for get_file_contents tool"""
    
    @staticmethod
    def generate_response(path: str, ref: str = "main") -> Dict[str, Any]:
        """Generate get_file_contents response"""
        file_type = "file"
        if path.endswith("/"):
            file_type = "dir"
        
        content = """#!/usr/bin/env python3
'''
Sample Python module

This is a demonstration file with typical Python code.
'''

def main():
    print("Hello, World!")

if __name__ == "__main__":
    main()
"""
        
        return {
            "name": path.split("/")[-1],
            "path": path,
            "sha": GetFileContentsMockGenerator.random_sha(),
            "size": len(content),
            "type": file_type,
            "content": content,
            "encoding": "utf-8",
            "url": f"https://api.github.com/repos/org/repo/contents/{path}",
            "html_url": f"https://github.com/org/repo/blob/{ref}/{path}",
        }


# ==============================================================================
# 5. GET COMMIT MOCK
# ==============================================================================

class GetCommitMockGenerator(MockDataGenerator):
    """Mock generator for get_commit tool"""
    
    @staticmethod
    def generate_response(sha: str) -> Dict[str, Any]:
        """Generate get_commit response"""
        return {
            "sha": sha,
            "message": "Fix: improve error handling in authentication module",
            "author": {
                "name": random.choice(["Alice", "Bob", "Charlie"]),
                "email": GetFileContentsMockGenerator.random_email(),
                "date": GetCommitMockGenerator.random_iso_date(days_ago=random.randint(0, 30)),
            },
            "committer": {
                "name": "GitHub",
                "email": "noreply@github.com",
                "date": GetCommitMockGenerator.random_iso_date(days_ago=random.randint(0, 30)),
            },
            "tree": {
                "sha": GetCommitMockGenerator.random_sha(),
                "url": f"https://api.github.com/repos/org/repo/git/trees/{GetCommitMockGenerator.random_sha()}",
            },
            "parents": [
                {
                    "sha": GetCommitMockGenerator.random_sha(),
                    "url": f"https://api.github.com/repos/org/repo/git/commits/{GetCommitMockGenerator.random_sha()}",
                }
            ],
            "url": f"https://api.github.com/repos/org/repo/git/commits/{sha}",
            "html_url": f"https://github.com/org/repo/commit/{sha}",
            "author_date": GetCommitMockGenerator.random_iso_date(days_ago=random.randint(0, 30)),
            "committer_date": GetCommitMockGenerator.random_iso_date(days_ago=random.randint(0, 30)),
        }


# ==============================================================================
# 6. LIST PULL REQUESTS MOCK
# ==============================================================================

class ListPRsMockGenerator(MockDataGenerator):
    """Mock generator for list_pull_requests tool"""
    
    @staticmethod
    def generate_pr() -> Dict[str, Any]:
        """Generate single PR item"""
        return {
            "id": random.randint(1000000, 9999999),
            "number": random.randint(100, 5000),
            "title": f"PR#{random.randint(1000, 5000)}: {random.choice(['Add', 'Fix', 'Improve'])} feature",
            "user": {
                "login": random.choice(["alice", "bob", "charlie"]),
                "id": random.randint(1000, 9999),
            },
            "state": random.choice(["open", "closed"]),
            "created_at": ListPRsMockGenerator.random_iso_date(days_ago=random.randint(0, 60)),
            "updated_at": ListPRsMockGenerator.random_iso_date(days_ago=random.randint(0, 30)),
            "closed_at": ListPRsMockGenerator.random_iso_date(days_ago=random.randint(0, 10)) if random.random() > 0.5 else None,
            "merged_at": ListPRsMockGenerator.random_iso_date(days_ago=random.randint(0, 10)) if random.random() > 0.7 else None,
            "mergeable": random.choice([True, False, None]),
            "draft": random.choice([True, False]),
        }
    
    @staticmethod
    def generate_response(per_page: int = 30) -> List[Dict[str, Any]]:
        """Generate list_pull_requests response"""
        return [ListPRsMockGenerator.generate_pr() for _ in range(min(per_page, 30))]


# ==============================================================================
# 7. PULL REQUEST READ (DETAILS) MOCK
# ==============================================================================

class PRReadMockGenerator(MockDataGenerator):
    """Mock generator for pull_request_read tool"""
    
    @staticmethod
    def generate_response(pr_number: int) -> Dict[str, Any]:
        """Generate PR details response"""
        return {
            "id": random.randint(1000000, 9999999),
            "number": pr_number,
            "title": f"Feature: Add authentication support (PR#{pr_number})",
            "body": "This PR adds OAuth2 authentication support with the following features:\n- User login\n- Token refresh\n- Session management",
            "user": {
                "login": random.choice(["alice", "bob", "charlie"]),
                "id": random.randint(1000, 9999),
            },
            "state": random.choice(["open", "closed"]),
            "created_at": PRReadMockGenerator.random_iso_date(days_ago=random.randint(0, 30)),
            "updated_at": PRReadMockGenerator.random_iso_date(days_ago=random.randint(0, 15)),
            "closed_at": PRReadMockGenerator.random_iso_date(days_ago=random.randint(0, 10)) if random.random() > 0.5 else None,
            "merged_at": PRReadMockGenerator.random_iso_date(days_ago=random.randint(0, 10)) if random.random() > 0.7 else None,
            "draft": False,
            "head": {
                "sha": PRReadMockGenerator.random_sha(),
                "ref": "feature/auth",
                "repo": {
                    "name": "repo",
                    "full_name": "org/repo",
                }
            },
            "base": {
                "sha": PRReadMockGenerator.random_sha(),
                "ref": "main",
            },
            "merge_commit_sha": PRReadMockGenerator.random_sha() if random.random() > 0.5 else None,
            "additions": random.randint(10, 500),
            "deletions": random.randint(5, 200),
            "changed_files": random.randint(1, 20),
            "comments": random.randint(0, 50),
            "review_comments": random.randint(0, 30),
            "commits": random.randint(1, 20),
        }


# ==============================================================================
# 8. ISSUE READ (DETAILS) MOCK
# ==============================================================================

class IssueReadMockGenerator(MockDataGenerator):
    """Mock generator for issue_read tool"""
    
    @staticmethod
    def generate_response(issue_number: int) -> Dict[str, Any]:
        """Generate issue details response"""
        return {
            "id": random.randint(1000000, 9999999),
            "number": issue_number,
            "title": f"Bug: Error in authentication flow (Issue#{issue_number})",
            "body": "When trying to authenticate with invalid credentials, the API returns a 500 error instead of 401.",
            "user": {
                "login": random.choice(["alice", "bob", "charlie"]),
                "id": random.randint(1000, 9999),
            },
            "state": random.choice(["open", "closed"]),
            "labels": [
                {"name": "bug"},
                {"name": "priority-high"},
            ],
            "created_at": IssueReadMockGenerator.random_iso_date(days_ago=random.randint(0, 30)),
            "updated_at": IssueReadMockGenerator.random_iso_date(days_ago=random.randint(0, 10)),
            "closed_at": IssueReadMockGenerator.random_iso_date(days_ago=random.randint(0, 5)) if random.random() > 0.5 else None,
            "comments": random.randint(0, 20),
            "assignee": {
                "login": random.choice(["alice", "bob", "charlie"]),
                "id": random.randint(1000, 9999),
            } if random.random() > 0.3 else None,
            "milestone": {
                "number": random.randint(1, 10),
                "title": f"v{random.randint(1, 3)}.{random.randint(0, 9)}.0",
            } if random.random() > 0.5 else None,
        }


# ==============================================================================
# 9. LIST WORKFLOWS MOCK
# ==============================================================================

class ListWorkflowsMockGenerator(MockDataGenerator):
    """Mock generator for list_workflows tool"""
    
    @staticmethod
    def generate_workflow() -> Dict[str, Any]:
        """Generate workflow item"""
        workflow_names = ["CI", "Tests", "Build", "Security", "Documentation", "Deploy"]
        
        return {
            "id": random.randint(1000000, 9999999),
            "name": random.choice(workflow_names),
            "path": f".github/workflows/{random.choice(workflow_names).lower()}.yml",
            "state": random.choice(["active", "deleted"]),
            "created_at": ListWorkflowsMockGenerator.random_iso_date(days_ago=random.randint(0, 365)),
            "updated_at": ListWorkflowsMockGenerator.random_iso_date(days_ago=random.randint(0, 30)),
            "url": f"https://api.github.com/repos/org/repo/actions/workflows/{random.randint(1000000, 9999999)}",
            "html_url": "https://github.com/org/repo/blob/main/.github/workflows/test.yml",
            "badge_url": "https://github.com/org/repo/workflows/CI/badge.svg",
        }
    
    @staticmethod
    def generate_response(per_page: int = 30) -> Dict[str, Any]:
        """Generate list_workflows response"""
        return {
            "total_count": random.randint(5, 20),
            "workflows": [ListWorkflowsMockGenerator.generate_workflow() for _ in range(min(per_page, 10))],
        }


# ==============================================================================
# 10. GET WORKFLOW RUN MOCK
# ==============================================================================

class GetWorkflowRunMockGenerator(MockDataGenerator):
    """Mock generator for get_workflow_run tool"""
    
    @staticmethod
    def generate_response(run_id: int) -> Dict[str, Any]:
        """Generate workflow run details"""
        statuses = ["queued", "in_progress", "completed"]
        conclusions = ["success", "failure", "neutral", "cancelled", "skipped", "action_required"]
        
        return {
            "id": run_id,
            "name": random.choice(["CI Pipeline", "Tests", "Build & Deploy"]),
            "node_id": "MDg6Q2hlY2tSdW57MzEwMDF9",
            "head_branch": "main",
            "head_sha": GetWorkflowRunMockGenerator.random_sha(),
            "path": ".github/workflows/ci.yml",
            "display_title": f"Workflow run #{run_id}",
            "run_number": run_id,
            "event": "push",
            "status": random.choice(statuses),
            "conclusion": random.choice(conclusions) if random.random() > 0.3 else None,
            "workflow_id": random.randint(1000000, 9999999),
            "check_suite_id": random.randint(1000000000, 9999999999),
            "check_suite_node_id": "MDExOkNoZWNrU3VpdGU4MjM5MDI4",
            "url": f"https://api.github.com/repos/org/repo/actions/runs/{run_id}",
            "html_url": f"https://github.com/org/repo/actions/runs/{run_id}",
            "pull_requests": [],
            "created_at": GetWorkflowRunMockGenerator.random_iso_date(days_ago=random.randint(0, 30)),
            "updated_at": GetWorkflowRunMockGenerator.random_iso_date(days_ago=random.randint(0, 10)),
            "actor": {
                "login": "alice",
                "id": random.randint(1000, 9999),
            },
            "run_attempt": 1,
            "referenced_workflows": [],
            "head_commit": {
                "id": GetWorkflowRunMockGenerator.random_sha(),
                "tree_id": GetWorkflowRunMockGenerator.random_sha(),
                "message": "Update documentation",
                "timestamp": GetWorkflowRunMockGenerator.random_iso_date(days_ago=1),
                "author": {
                    "name": "Alice",
                    "email": "alice@example.com",
                },
            },
            "repository": {
                "id": random.randint(1000000, 9999999),
                "name": "repo",
                "full_name": "org/repo",
            },
            "head_repository": {
                "id": random.randint(1000000, 9999999),
                "name": "repo",
                "full_name": "org/repo",
            },
        }


# ==============================================================================
# 11. GET JOB LOGS MOCK
# ==============================================================================

class GetJobLogsMockGenerator(MockDataGenerator):
    """Mock generator for get_job_logs tool"""
    
    @staticmethod
    def generate_response(job_id: int) -> str:
        """Generate job logs"""
        return """
Run #1234 - Job #5678
2026-07-02T10:30:15.123Z
Current runner version: '2.298.0'
GitHub Actions runtime token ACs refresh
Setting up auth for https://github.com
Getting credentials from user input
Sanitizing any log output now
Setting up the workflow
Processing secret files
Removing old release assets
Creating new release
Asset 'app-1.0.0-linux-x64.tar.gz' created
Uploading artifact 'dist'
Task completed successfully!
"""


# ==============================================================================
# 12. SEARCH REPOSITORIES MOCK
# ==============================================================================

class SearchRepositoriesMockGenerator(MockDataGenerator):
    """Mock generator for search_repositories tool"""
    
    @staticmethod
    def generate_repo() -> Dict[str, Any]:
        """Generate repository item"""
        return {
            "id": random.randint(1000000, 999999999),
            "node_id": "MDEwOlJlcG9zaXRvcnkxMjk2MjY5",
            "name": f"repo-{random.randint(1, 1000)}",
            "full_name": f"org/repo-{random.randint(1, 1000)}",
            "private": False,
            "owner": {
                "login": "org",
                "id": random.randint(1000000, 9999999),
            },
            "html_url": f"https://github.com/org/repo-{random.randint(1, 1000)}",
            "description": "A sample repository for demonstration",
            "fork": False,
            "created_at": SearchRepositoriesMockGenerator.random_iso_date(days_ago=random.randint(0, 365)),
            "updated_at": SearchRepositoriesMockGenerator.random_iso_date(days_ago=random.randint(0, 60)),
            "pushed_at": SearchRepositoriesMockGenerator.random_iso_date(days_ago=random.randint(0, 30)),
            "size": random.randint(100, 10000),
            "stargazers_count": random.randint(0, 5000),
            "watchers_count": random.randint(0, 1000),
            "language": random.choice(["Python", "JavaScript", "Go", "Rust", "Java", "C++"]),
            "forks_count": random.randint(0, 500),
            "open_issues_count": random.randint(0, 100),
            "default_branch": "main",
            "score": round(random.uniform(1.0, 100.0), 2),
        }
    
    @staticmethod
    def generate_response(query: str, results: int = 10) -> Dict[str, Any]:
        """Generate search_repositories response"""
        return {
            "total_count": random.randint(100, 10000),
            "incomplete_results": False,
            "items": [SearchRepositoriesMockGenerator.generate_repo() for _ in range(results)]
        }


# Export all generators
__all__ = [
    "SearchCodeMockGenerator",
    "SearchIssuesMockGenerator",
    "SearchPRsMockGenerator",
    "GetFileContentsMockGenerator",
    "GetCommitMockGenerator",
    "ListPRsMockGenerator",
    "PRReadMockGenerator",
    "IssueReadMockGenerator",
    "ListWorkflowsMockGenerator",
    "GetWorkflowRunMockGenerator",
    "GetJobLogsMockGenerator",
    "SearchRepositoriesMockGenerator",
]
