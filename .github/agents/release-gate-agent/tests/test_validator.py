"""
Tests for Release Gate Agent - Validator Module (PERCEIVE Phase)

#AFTERMATH_PATTERN_IDENTIFIED: release_gate_testing
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from agent.validator import ReleaseValidator, ValidationResult


class TestValidationResult:
    """Test ValidationResult dataclass."""
    
    def test_validation_result_creation(self):
        """Test creating ValidationResult with all fields."""
        result = ValidationResult(
            check_name="Test Check",
            passed=True,
            score=0.95,
            details={"test": "data"},
            error_message=""
        )
        
        assert result.check_name == "Test Check"
        assert result.passed is True
        assert result.score == 0.95
        assert result.details == {"test": "data"}
        assert result.timestamp is not None
    
    def test_validation_result_default_timestamp(self):
        """Test ValidationResult creates timestamp automatically."""
        result = ValidationResult(
            check_name="Test",
            passed=True,
            score=1.0,
            details={}
        )
        
        assert result.timestamp is not None


class TestReleaseValidator:
    """Test ReleaseValidator class."""
    
    @pytest.fixture
    def mock_brain(self):
        """Mock CognitiveBrain."""
        with patch('agent.validator.CognitiveBrain') as mock:
            yield mock
    
    @pytest.fixture
    def validator(self, mock_brain, tmp_path):
        """Create ReleaseValidator instance with mocked brain."""
        return ReleaseValidator(tmp_path, branch="test-branch")
    
    def test_validator_initialization(self, validator, tmp_path):
        """Test ReleaseValidator initializes correctly."""
        assert validator.repo_path == tmp_path
        assert validator.branch == "test-branch"
        assert validator.validations == []
    
    def test_perceive_returns_validation_results(self, validator):
        """Test perceive() returns properly formatted results."""
        release_info = {"version": "v1.0.0"}
        
        with patch.object(validator, '_check_ci_pipelines') as mock_ci, \
             patch.object(validator, '_analyze_test_coverage') as mock_coverage, \
             patch.object(validator, '_get_security_scan_results') as mock_security, \
             patch.object(validator, '_audit_dependencies') as mock_deps, \
             patch.object(validator, '_detect_breaking_changes') as mock_breaking, \
             patch.object(validator, '_verify_documentation') as mock_docs:
            
            # Mock all validation checks to pass
            for mock_check in [mock_ci, mock_coverage, mock_security, mock_deps, mock_breaking, mock_docs]:
                mock_check.return_value = ValidationResult(
                    check_name="Test", passed=True, score=1.0, details={}
                )
            
            result = validator.perceive(release_info)
            
            assert "validations" in result
            assert "pass_rate" in result
            assert "total_checks" in result
            assert "passed_checks" in result
            assert result["pass_rate"] == 1.0
            assert result["total_checks"] == 6
            assert result["passed_checks"] == 6
    
    def test_check_ci_pipelines_success(self, validator):
        """Test CI pipeline check with successful run."""
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = b'[{"conclusion": "success", "status": "completed"}]'
        
        with patch('subprocess.run', return_value=mock_result):
            result = validator._check_ci_pipelines()
            
            assert result.check_name == "CI/CD Status"
            assert result.passed is True
            assert result.score == 1.0
    
    def test_check_ci_pipelines_failure(self, validator):
        """Test CI pipeline check with failed run."""
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = b'[{"conclusion": "failure", "status": "completed"}]'
        
        with patch('subprocess.run', return_value=mock_result):
            result = validator._check_ci_pipelines()
            
            assert result.check_name == "CI/CD Status"
            assert result.passed is False
            assert result.score == 0.0
    
    def test_check_ci_pipelines_timeout(self, validator):
        """Test CI pipeline check handles timeout gracefully."""
        with patch('subprocess.run', side_effect=TimeoutError("Timeout")):
            result = validator._check_ci_pipelines()
            
            assert result.check_name == "CI/CD Status"
            assert result.passed is False
            assert "CI check failed" in result.error_message
    
    def test_analyze_test_coverage_file_exists(self, validator, tmp_path):
        """Test coverage analysis when .coverage file exists."""
        coverage_file = tmp_path / ".coverage"
        coverage_file.touch()
        
        result = validator._analyze_test_coverage()
        
        assert result.check_name == "Test Coverage"
        assert result.passed is True
        assert result.score == 0.92
    
    def test_analyze_test_coverage_file_missing(self, validator):
        """Test coverage analysis when .coverage file is missing."""
        result = validator._analyze_test_coverage()
        
        assert result.check_name == "Test Coverage"
        assert result.passed is False
        assert "No coverage report found" in result.error_message
    
    def test_get_security_scan_results(self, validator):
        """Test security scan results retrieval."""
        with patch.object(validator.brain, 'query_patterns', return_value=[]):
            result = validator._get_security_scan_results()
            
            assert result.check_name == "Security Scan"
            assert result.passed is True
            assert result.score == 1.0
    
    def test_get_security_scan_critical_vulns(self, validator):
        """Test security scan with critical vulnerabilities."""
        critical_patterns = [
            {"severity": "critical", "cve": "CVE-2024-0001"},
            {"severity": "high", "cve": "CVE-2024-0002"}
        ]
        
        with patch.object(validator.brain, 'query_patterns', return_value=critical_patterns):
            result = validator._get_security_scan_results()
            
            assert result.check_name == "Security Scan"
            assert result.passed is False
            assert result.score == 0.0
            assert result.details["critical_vulnerabilities"] == 1
    
    def test_verify_documentation_all_present(self, validator, tmp_path):
        """Test documentation verification when all files present."""
        (tmp_path / "README.md").touch()
        (tmp_path / "CHANGELOG.md").touch()
        (tmp_path / "docs").mkdir()
        
        result = validator._verify_documentation()
        
        assert result.check_name == "Documentation Completeness"
        assert result.passed is True
        assert result.score == 1.0
    
    def test_verify_documentation_missing_files(self, validator):
        """Test documentation verification with missing files."""
        result = validator._verify_documentation()
        
        assert result.check_name == "Documentation Completeness"
        assert result.passed is False
        assert len(result.details["missing_docs"]) > 0
    
    def test_to_dict_conversion(self, validator):
        """Test ValidationResult to dict conversion."""
        validation = ValidationResult(
            check_name="Test",
            passed=True,
            score=0.9,
            details={"key": "value"},
            error_message="test error"
        )
        
        result_dict = validator._to_dict(validation)
        
        assert result_dict["check_name"] == "Test"
        assert result_dict["passed"] is True
        assert result_dict["score"] == 0.9
        assert result_dict["details"] == {"key": "value"}
        assert result_dict["error_message"] == "test error"
        assert "timestamp" in result_dict
