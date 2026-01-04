"""
Tests for AST Analysis Agent.

Comprehensive test suite covering:
- ASTAnalysisAgent functionality
- PatternDetector accuracy
- ReportGenerator output formats
"""
import os
import sys
import tempfile

# Add agent directory to path for imports
agent_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'agent')
sys.path.insert(0, agent_dir)

from analyzer import ASTAnalysisAgent, CodeFinding, AnalysisContext
from pattern_detector import PatternDetector
from report_generator import ReportGenerator, ReportConfig


class TestASTAnalysisAgent:
    """Tests for ASTAnalysisAgent."""
    
    def test_create_agent(self):
        """Test creating agent."""
        agent = ASTAnalysisAgent()
        assert agent.name == "ast-analysis"
        assert len(agent.analyzers) > 0
    
    def test_perceive_valid_code(self):
        """Test perceiving valid Python code."""
        agent = ASTAnalysisAgent()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("def foo():\n    pass\n")
            f.flush()
            
            context = agent.perceive(f.name)
            
            assert context.file_path == f.name
            assert context.ast_tree is not None
            assert len(context.findings) == 0
            
            os.unlink(f.name)
    
    def test_perceive_syntax_error(self):
        """Test perceiving code with syntax error."""
        agent = ASTAnalysisAgent()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("def foo(\n")  # Invalid syntax
            f.flush()
            
            context = agent.perceive(f.name)
            
            assert any(f.category == 'syntax' for f in context.findings)
            
            os.unlink(f.name)
    
    def test_decide_with_valid_code(self):
        """Test decision making for valid code."""
        agent = ASTAnalysisAgent()
        context = AnalysisContext(file_path="test.py")
        
        analyzers = agent.decide(context)
        
        assert len(analyzers) > 0
        assert 'complexity' in analyzers
    
    def test_decide_with_syntax_error(self):
        """Test decision making skips analysis on syntax error."""
        agent = ASTAnalysisAgent()
        context = AnalysisContext(file_path="test.py")
        context.findings.append(CodeFinding(
            file_path="test.py",
            line=1,
            column=0,
            severity='error',
            category='syntax',
            message='Syntax error',
        ))
        
        analyzers = agent.decide(context)
        
        assert len(analyzers) == 0
    
    def test_analyze_file(self):
        """Test full file analysis."""
        agent = ASTAnalysisAgent()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("def foo():\n    pass\n")
            f.flush()
            
            findings, summary = agent.analyze_file(f.name)
            
            assert isinstance(findings, list)
            assert 'findings_count' in summary
            assert agent.files_analyzed == 1
            
            os.unlink(f.name)
    
    def test_complexity_detection(self):
        """Test complexity analyzer."""
        agent = ASTAnalysisAgent(max_complexity=2)
        
        complex_code = '''
def complex_func(x):
    if x > 0:
        if x > 10:
            while x > 5:
                for i in range(x):
                    pass
    return x
'''
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(complex_code)
            f.flush()
            
            findings, _ = agent.analyze_file(f.name)
            
            complexity_findings = [f for f in findings if f.category == 'complexity']
            assert len(complexity_findings) > 0
            
            os.unlink(f.name)
    
    def test_naming_analyzer(self):
        """Test naming convention analyzer."""
        agent = ASTAnalysisAgent()
        
        bad_naming = '''
def BadFunction():
    pass

class lowercase_class:
    pass
'''
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(bad_naming)
            f.flush()
            
            findings, _ = agent.analyze_file(f.name)
            
            naming_findings = [f for f in findings if f.category == 'naming']
            assert len(naming_findings) > 0
            
            os.unlink(f.name)
    
    def test_get_statistics(self):
        """Test getting agent statistics."""
        agent = ASTAnalysisAgent()
        
        stats = agent.get_statistics()
        
        assert 'files_analyzed' in stats
        assert 'total_findings' in stats


class TestPatternDetector:
    """Tests for PatternDetector."""
    
    def test_create_detector(self):
        """Test creating detector."""
        detector = PatternDetector()
        assert len(detector.patterns) > 0
    
    def test_detect_singleton(self):
        """Test singleton pattern detection."""
        detector = PatternDetector()
        
        singleton_code = '''
class Singleton:
    _instance = None
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
'''
        detector.detect_patterns(singleton_code)
        
        singleton_patterns = [p for p in patterns if p.name == 'singleton']
        assert len(singleton_patterns) > 0
    
    def test_detect_factory(self):
        """Test factory pattern detection."""
        detector = PatternDetector()
        
        factory_code = '''
def create_user(name):
    return User(name)

def make_product(id):
    return Product(id)
'''
        patterns = detector.detect_patterns(factory_code)
        
        factory_patterns = [p for p in patterns if p.name == 'factory']
        assert len(factory_patterns) > 0
    
    def test_detect_god_class(self):
        """Test god class anti-pattern detection."""
        # Use default threshold of 20 methods
        detector = PatternDetector(god_class_method_threshold=20)
        
        # Create a class with more methods than threshold
        methods = "\n    ".join([f"def method_{i}(self): pass" for i in range(25)])
        god_class_code = f'''
class GodClass:
    {methods}
'''
        patterns = detector.detect_patterns(god_class_code)
        
        god_class_patterns = [p for p in patterns if p.name == 'god_class']
        assert len(god_class_patterns) > 0
    
    def test_detect_long_params(self):
        """Test long parameter list detection."""
        detector = PatternDetector()
        
        long_params_code = '''
def long_function(a, b, c, d, e, f, g, h):
    pass
'''
        patterns = detector.detect_patterns(long_params_code)
        
        long_param_patterns = [p for p in patterns if p.name == 'long_parameter_list']
        assert len(long_param_patterns) > 0
    
    def test_detect_decorator(self):
        """Test decorator pattern detection."""
        detector = PatternDetector()
        
        decorator_code = '''
@decorator
def decorated_function():
    pass

@another_decorator(arg=1)
def another_function():
    pass
'''
        patterns = detector.detect_patterns(decorator_code)
        
        decorator_patterns = [p for p in patterns if p.name == 'decorator_pattern']
        assert len(decorator_patterns) == 2
    
    def test_get_statistics(self):
        """Test getting statistics."""
        detector = PatternDetector()
        detector.detect_patterns("def create_x(): return X()")
        
        stats = detector.get_statistics()
        
        assert 'total_patterns' in stats
        assert 'by_category' in stats


class TestReportGenerator:
    """Tests for ReportGenerator."""
    
    def test_create_generator(self):
        """Test creating generator."""
        generator = ReportGenerator()
        assert generator.config.format == "markdown"
    
    def test_generate_markdown(self):
        """Test markdown report generation."""
        generator = ReportGenerator(ReportConfig(format="markdown"))
        
        findings = [
            {
                'file_path': 'test.py',
                'line': 10,
                'column': 0,
                'severity': 'warning',
                'category': 'complexity',
                'message': 'High complexity',
            }
        ]
        
        report = generator.generate(findings)
        
        assert "# AST Analysis Report" in report
        assert "warning" in report.lower()
        assert "complexity" in report.lower()
    
    def test_generate_json(self):
        """Test JSON report generation."""
        generator = ReportGenerator(ReportConfig(format="json"))
        
        findings = [
            {'file_path': 'test.py', 'severity': 'error', 'category': 'syntax', 'message': 'Error'}
        ]
        
        report = generator.generate(findings)
        
        import json
        data = json.loads(report)
        assert 'findings' in data
        assert len(data['findings']) == 1
    
    def test_generate_csv(self):
        """Test CSV report generation."""
        generator = ReportGenerator(ReportConfig(format="csv"))
        
        findings = [
            {'file_path': 'test.py', 'line': 1, 'severity': 'warning', 'category': 'style', 'message': 'Style issue'}
        ]
        
        report = generator.generate(findings)
        
        assert "file_path" in report
        assert "test.py" in report
    
    def test_generate_html(self):
        """Test HTML report generation."""
        generator = ReportGenerator(ReportConfig(format="html"))
        
        findings = [
            {'file_path': 'test.py', 'severity': 'info', 'category': 'naming', 'message': 'Naming issue'}
        ]
        
        report = generator.generate(findings)
        
        assert "<html>" in report
        assert "test.py" in report
    
    def test_severity_filter(self):
        """Test filtering by severity."""
        config = ReportConfig(format="json", severity_filter=["error"])
        generator = ReportGenerator(config)
        
        findings = [
            {'severity': 'error', 'message': 'Error'},
            {'severity': 'warning', 'message': 'Warning'},
        ]
        
        report = generator.generate(findings)
        
        import json
        data = json.loads(report)
        assert len(data['findings']) == 1
        assert data['findings'][0]['severity'] == 'error'
    
    def test_category_filter(self):
        """Test filtering by category."""
        config = ReportConfig(format="json", category_filter=["security"])
        generator = ReportGenerator(config)
        
        findings = [
            {'category': 'security', 'message': 'Security issue'},
            {'category': 'style', 'message': 'Style issue'},
        ]
        
        report = generator.generate(findings)
        
        import json
        data = json.loads(report)
        assert len(data['findings']) == 1
        assert data['findings'][0]['category'] == 'security'
    
    def test_empty_findings(self):
        """Test report with no findings."""
        generator = ReportGenerator()
        
        report = generator.generate([])
        
        assert "Total Findings:** 0" in report or "total_findings" in report.lower()


class TestIntegration:
    """Integration tests."""
    
    def test_full_analysis_pipeline(self):
        """Test full analysis pipeline."""
        agent = ASTAnalysisAgent()
        detector = PatternDetector()
        generator = ReportGenerator()
        
        code = '''
class MyClass:
    def __init__(self):
        pass
    
    def badNaming(self):
        pass
'''
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            f.flush()
            
            # Analyze
            findings, summary = agent.analyze_file(f.name)
            
            # Detect patterns
            patterns = detector.detect_patterns(code)
            
            # Generate report
            report = generator.generate([f.to_dict() for f in findings])
            
            assert isinstance(report, str)
            assert len(report) > 0
            
            os.unlink(f.name)
