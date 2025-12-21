"""Tests for autonomous self-review protocol."""
from pathlib import Path
import json
import sys

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from ai_self_review_protocol import (
    SelfReviewProtocol, Issue, IssueType, Priority, ReviewStatus, ReviewCycle
)
from code_change_reviewer import CodeChangeReviewer


def test_issue_creation():
    """Test Issue dataclass creation."""
    issue = Issue(
        id="test123",
        type=IssueType.GAP,
        priority=Priority.HIGH,
        description="Test gap",
        location="test.py",
        discovered_at="2025-12-21T00:00:00"
    )
    
    assert issue.id == "test123"
    assert issue.type == IssueType.GAP
    assert issue.priority == Priority.HIGH
    assert not issue.fixed


def test_issue_auto_id_generation():
    """Test automatic ID generation for issues."""
    issue = Issue(
        id="",  # Empty, should be auto-generated
        type=IssueType.RISK,
        priority=Priority.CRITICAL,
        description="Security risk",
        location="app.py",
        discovered_at="2025-12-21T00:00:00"
    )
    
    assert issue.id
    assert len(issue.id) == 12  # MD5 truncated to 12 chars


def test_protocol_initialization():
    """Test SelfReviewProtocol initialization."""
    protocol = SelfReviewProtocol("Test task")
    
    assert protocol.task_description == "Test task"
    assert protocol.report.session_id
    assert len(protocol.report.session_id) == 16
    assert protocol.report.status == ReviewStatus.DRAFT
    assert protocol.current_cycle == 0


def test_start_cycle():
    """Test starting a review cycle."""
    protocol = SelfReviewProtocol("Test task")
    
    cycle = protocol.start_cycle()
    
    assert isinstance(cycle, ReviewCycle)
    assert cycle.cycle_number == 1
    assert protocol.current_cycle == 1
    assert protocol.report.status == ReviewStatus.IN_REVIEW
    assert len(protocol.report.cycles) == 1


def test_identify_issue():
    """Test issue identification."""
    protocol = SelfReviewProtocol("Test task")
    protocol.start_cycle()
    
    issue = protocol.identify_issue(
        IssueType.MISSING_TEST,
        Priority.HIGH,
        "No tests for module",
        "src/module.py"
    )
    
    assert issue.id in protocol.all_issues
    assert protocol.report.total_issues_identified == 1
    assert len(protocol.report.cycles[-1].issues_identified) == 1


def test_fix_issue():
    """Test fixing an issue."""
    protocol = SelfReviewProtocol("Test task")
    protocol.start_cycle()
    
    issue = protocol.identify_issue(
        IssueType.GAP,
        Priority.HIGH,
        "Missing feature",
        "src/app.py"
    )
    
    success = protocol.fix_issue(issue.id, "Implemented missing feature")
    
    assert success
    assert protocol.all_issues[issue.id].fixed
    assert protocol.all_issues[issue.id].fix_description == "Implemented missing feature"
    assert protocol.report.total_issues_fixed == 1


def test_defer_issue():
    """Test deferring an issue."""
    protocol = SelfReviewProtocol("Test task")
    protocol.start_cycle()
    
    issue = protocol.identify_issue(
        IssueType.OPTIMIZATION,
        Priority.LOW,
        "Could optimize algorithm",
        "src/utils.py"
    )
    
    success = protocol.defer_issue(issue.id, "Will optimize in separate PR")
    
    assert success
    assert protocol.all_issues[issue.id].mitigation == "Will optimize in separate PR"
    assert protocol.report.total_issues_deferred == 1


def test_validate_fix():
    """Test validating a fix."""
    protocol = SelfReviewProtocol("Test task")
    protocol.start_cycle()
    
    issue = protocol.identify_issue(
        IssueType.RISK,
        Priority.CRITICAL,
        "Security vulnerability",
        "src/auth.py"
    )
    
    protocol.fix_issue(issue.id, "Added input validation")
    success = protocol.validate_fix(issue.id, "Tests passing")
    
    assert success
    assert protocol.all_issues[issue.id].validation_status == "Tests passing"


def test_calculate_convergence():
    """Test convergence calculation."""
    protocol = SelfReviewProtocol("Test task")
    protocol.start_cycle()
    
    # Add 2 high-priority issues
    issue1 = protocol.identify_issue(
        IssueType.GAP, Priority.HIGH, "Gap 1", "file1.py"
    )
    issue2 = protocol.identify_issue(
        IssueType.RISK, Priority.HIGH, "Risk 1", "file2.py"
    )
    
    # Initial convergence should be 0%
    assert protocol.calculate_convergence() == 0.0
    
    # Fix one issue
    protocol.fix_issue(issue1.id, "Fixed gap")
    assert protocol.calculate_convergence() == 0.5
    
    # Fix both issues
    protocol.fix_issue(issue2.id, "Mitigated risk")
    assert protocol.calculate_convergence() == 1.0


def test_check_convergence_minimum_cycles():
    """Test that minimum cycles are required."""
    protocol = SelfReviewProtocol("Test task")
    
    # First cycle
    protocol.start_cycle()
    protocol.complete_cycle(["Initial work"])
    
    # Should not converge yet (need 2 cycles minimum)
    converged, reason = protocol.check_convergence()
    assert not converged
    assert "at least 2 cycles" in reason.lower()


def test_check_convergence_critical_issues():
    """Test that critical issues prevent convergence."""
    protocol = SelfReviewProtocol("Test task")
    
    # Cycle 1
    protocol.start_cycle()
    protocol.identify_issue(
        IssueType.RISK, Priority.CRITICAL, "Critical bug", "app.py"
    )
    protocol.complete_cycle(["Identified issues"])
    
    # Cycle 2
    protocol.start_cycle()
    protocol.complete_cycle(["No fixes"])
    
    # Should not converge with unfixed critical issue
    converged, reason = protocol.check_convergence()
    assert not converged
    assert "critical" in reason.lower()


def test_check_convergence_success():
    """Test successful convergence."""
    protocol = SelfReviewProtocol("Test task")
    
    # Cycle 1
    protocol.start_cycle()
    issue = protocol.identify_issue(
        IssueType.GAP, Priority.HIGH, "Gap", "file.py"
    )
    protocol.complete_cycle(["Identified issues"])
    
    # Cycle 2
    protocol.start_cycle()
    protocol.fix_issue(issue.id, "Fixed gap")
    protocol.complete_cycle(["Fixed issues"])
    
    # Should converge
    converged, reason = protocol.check_convergence()
    assert converged


def test_complete_cycle():
    """Test completing a review cycle."""
    protocol = SelfReviewProtocol("Test task")
    
    protocol.start_cycle()
    changes = ["Change 1", "Change 2"]
    cycle = protocol.complete_cycle(changes)
    
    assert cycle.completed_at is not None
    assert cycle.changes_made == changes
    assert cycle.convergence_score >= 0.0


def test_finalize_review():
    """Test finalizing the review."""
    protocol = SelfReviewProtocol("Test task")
    
    # Run cycles
    protocol.start_cycle()
    protocol.complete_cycle(["Work done"])
    
    protocol.start_cycle()
    protocol.complete_cycle(["More work"])
    
    # Finalize
    report = protocol.finalize_review("Task completed successfully")
    
    assert report.completed_at is not None
    assert report.status == ReviewStatus.COMPLETE
    assert report.final_notes == "Task completed successfully"


def test_production_readiness():
    """Test production readiness determination."""
    protocol = SelfReviewProtocol("Test task")
    
    # Cycle 1: Identify high-priority issue
    protocol.start_cycle()
    issue = protocol.identify_issue(
        IssueType.GAP, Priority.HIGH, "Gap", "file.py"
    )
    protocol.complete_cycle(["Identified"])
    
    # Cycle 2: Don't fix - should not be production ready
    protocol.start_cycle()
    protocol.complete_cycle(["No fixes"])
    protocol.finalize_review()
    
    assert not protocol.report.production_ready
    
    # Fix the issue
    protocol.fix_issue(issue.id, "Fixed")
    protocol.finalize_review()
    
    assert protocol.report.production_ready


def test_save_report(tmp_path):
    """Test saving review report."""
    protocol = SelfReviewProtocol("Test task", output_dir=tmp_path)
    
    protocol.start_cycle()
    protocol.complete_cycle(["Work done"])
    protocol.finalize_review()
    
    report_path = protocol.save_report()
    
    assert report_path.exists()
    assert report_path.suffix == ".json"
    
    # Verify JSON is valid
    with open(report_path) as f:
        data = json.load(f)
    
    assert data["session_id"] == protocol.report.session_id
    assert data["task_description"] == "Test task"


def test_report_to_dict():
    """Test converting report to dictionary."""
    protocol = SelfReviewProtocol("Test task")
    
    protocol.start_cycle()
    protocol.identify_issue(
        IssueType.GAP, Priority.HIGH, "Gap", "file.py"
    )
    protocol.complete_cycle(["Work"])
    protocol.finalize_review()
    
    report_dict = protocol._to_dict()
    
    assert isinstance(report_dict, dict)
    assert "session_id" in report_dict
    assert "cycles" in report_dict
    assert isinstance(report_dict["status"], str)


def test_code_change_reviewer_init(tmp_path):
    """Test CodeChangeReviewer initialization."""
    reviewer = CodeChangeReviewer(tmp_path)
    
    assert reviewer.repo_path == tmp_path
    assert reviewer.protocol is None


def test_analyze_python_file_docstrings(tmp_path):
    """Test Python file analysis for missing docstrings."""
    # Create test file without docstrings
    test_file = tmp_path / "test.py"
    test_file.write_text("""
class MyClass:
    def method(self):
        pass

def my_function():
    pass
""")
    
    reviewer = CodeChangeReviewer(tmp_path)
    issues = reviewer.analyze_python_file(test_file)
    
    # Should find missing docstrings
    assert len(issues) >= 2
    assert any("docstring" in issue[2].lower() for issue in issues)


def test_analyze_python_file_bare_except(tmp_path):
    """Test detection of bare except clauses."""
    test_file = tmp_path / "test.py"
    test_file.write_text("""
def risky_function():
    try:
        dangerous_operation()
    except:
        pass
""")
    
    reviewer = CodeChangeReviewer(tmp_path)
    issues = reviewer.analyze_python_file(test_file)
    
    # Should find bare except
    assert any("bare except" in issue[2].lower() for issue in issues)
    assert any(issue[1] == Priority.HIGH for issue in issues)


def test_analyze_python_file_todo_comments(tmp_path):
    """Test detection of TODO/FIXME comments."""
    test_file = tmp_path / "test.py"
    test_file.write_text("""
def my_function():
    # TODO: Implement this
    pass
    # FIXME: Bug here
""")
    
    reviewer = CodeChangeReviewer(tmp_path)
    issues = reviewer.analyze_python_file(test_file)
    
    # Should find TODO/FIXME
    assert any("todo" in issue[2].lower() or "fixme" in issue[2].lower() for issue in issues)


def test_check_test_coverage(tmp_path):
    """Test test coverage checking."""
    # Create source file without test
    src_dir = tmp_path / "src"
    src_dir.mkdir()
    (src_dir / "module.py").write_text("def function(): pass")
    
    reviewer = CodeChangeReviewer(tmp_path)
    issues = reviewer.check_test_coverage([src_dir / "module.py"])
    
    # Should find missing test
    assert len(issues) == 1
    assert issues[0][0] == IssueType.MISSING_TEST
    assert issues[0][1] == Priority.HIGH


def test_priority_enum_ordering():
    """Test that Priority enum has correct ordering."""
    assert Priority.CRITICAL.value < Priority.HIGH.value
    assert Priority.HIGH.value < Priority.MEDIUM.value
    assert Priority.MEDIUM.value < Priority.LOW.value


def test_multiple_cycles_convergence():
    """Test convergence over multiple cycles."""
    protocol = SelfReviewProtocol("Test task")
    
    # Cycle 1: Identify 3 issues
    protocol.start_cycle()
    issue1 = protocol.identify_issue(IssueType.GAP, Priority.HIGH, "Gap 1", "f1.py")
    issue2 = protocol.identify_issue(IssueType.GAP, Priority.HIGH, "Gap 2", "f2.py")
    issue3 = protocol.identify_issue(IssueType.GAP, Priority.HIGH, "Gap 3", "f3.py")
    protocol.complete_cycle(["Identified 3 issues"])
    
    assert protocol.calculate_convergence() == 0.0
    
    # Cycle 2: Fix 2 issues
    protocol.start_cycle()
    protocol.fix_issue(issue1.id, "Fixed 1")
    protocol.fix_issue(issue2.id, "Fixed 2")
    protocol.complete_cycle(["Fixed 2 issues"])
    
    assert abs(protocol.calculate_convergence() - 0.667) < 0.01
    
    # Cycle 3: Fix remaining issue
    protocol.start_cycle()
    protocol.fix_issue(issue3.id, "Fixed 3")
    protocol.complete_cycle(["Fixed remaining issue"])
    
    assert protocol.calculate_convergence() == 1.0
    
    # Should converge now
    converged, reason = protocol.check_convergence()
    assert converged
