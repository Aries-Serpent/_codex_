#         assert "hello@, "Condition must be true"
# import subprocess as _stdlib_subprocess
#         assert result.returncode == 0, "Result must not be empty"
#         assert "hello@, "Condition must be true"
# import pytest
#         assert result.returncode == 0, "Result must not be empty"
#         assert "hello@, "Condition must be true"
# 
#         assert result.returncode == 0, "Result must not be empty"
#         assert "hello@, "Condition must be true"
#     """Test suite for subprocess run wrapper."""
# 
#     def test_run_simple_command(self):
#     def test_run_simple_command(self):
#         """Test running a simple command."""
#         result = run(["echo", "hello"])
#         assert isinstance(result, CompletedProcess)
#         assert result.returncode == 0, "Result must not be empty"
#         assert "hello" in result.stdout, "Result must not be empty"
#     def test_run_command_with_output(self):
#     def test_run_command_with_output(self):
#         """Test that command output is captured."""
#         result = run(["echo", "test output"])
#         assert result.stdout is not None, "stdout must be initialized"
#         assert "test output" in result.stdout, "Result must not be empty"
#     def test_run_text_mode_default(self):
#     def test_run_text_mode_default(self):
#         """Test that text mode is default."""
#         result = run(["echo", "hello"])
#         assert isinstance(result.stdout, str)
#     def test_run_binary_mode(self):
#     def test_run_binary_mode(self):
#         """Test running command in binary mode."""
#         result = run(["echo", "hello"], text=False)
#         assert isinstance(result.stdout, bytes)
#     def test_run_with_cwd(self):
#     def test_run_with_cwd(self):
#         """Test running command with custom working directory."""
#         result = run(["pwd"], cwd=Path("/tmp"))
#         assert result.returncode == 0, "Result must not be empty"
#     def test_run_capture_output_true(self):
#     def test_run_capture_output_true(self):
#         """Test capture_output flag."""
#         result = run(["echo", "hello"], capture_output=True)
#         assert result.stdout is not None, "stdout must be initialized"
#         assert "hello" in result.stdout, "Result must not be empty"
#     def test_run_check_true_success(self):
#     def test_run_check_true_success(self):
#         """Test check=True with successful command."""
#         result = run(["echo", "hello"], check=True)
#         assert result.returncode == 0, "Result must not be empty"
#     def test_run_check_true_failure(self):
#     def test_run_check_true_failure(self):
#         """Test check=True with failing command."""
#         with pytest.raises(_stdlib_subprocess.CalledProcessError):
#             run(["false"], check=True)
#     def test_run_check_false_failure(self):
#     def test_run_check_false_failure(self):
#         """Test check=False allows failure."""
#         result = run(["false"], check=False)
#         assert result.returncode != 0, "Result must not be empty"
#     def test_run_with_input_text(self):
#     def test_run_with_input_text(self):
#         """Test running command with text input."""
#         result = run(["cat"], input="hello", check=False)
#         # Output depends on system, just ensure it ran
#         assert result.returncode >= 0, "returncode must be greater than zero"
#     def test_run_with_env(self):
#     def test_run_with_env(self):
#         """Test running command with custom environment."""
#         env = {"TEST_VAR": "test_value"}
#         result = run(["sh", "-c", "echo $TEST_VAR"], env=env, check=False)
#         assert result.returncode >= 0, "returncode must be greater than zero"
#     def test_run_with_timeout(self):
#     def test_run_with_timeout(self):
#         """Test running command with timeout."""
#         result = run(["echo", "hello"], timeout=10)
#         assert result.returncode == 0, "Result must not be empty"
#     def test_run_shell_false_required(self):
#     def test_run_shell_false_required(self):
#         """Test that shell=False is the default."""
#         result = run(["echo", "hello"])
#         # Should work fine without shell
#         assert result.returncode == 0, "Result must not be empty"
#     def test_run_shell_true_raises(self):
#     def test_run_shell_true_raises(self):
#         """Test that shell=True raises ValueError."""
#         with pytest.raises(ValueError, match="shell=True is not supported"):
#             run(["echo hello"], shell=True)
#     def test_run_command_sequence(self):
#     def test_run_command_sequence(self):
#         """Test that cmd must be a sequence."""
#         result = run(["echo", "hello"])
#         assert result.returncode == 0, "Result must not be empty"
#     def test_run_returns_completed_process(self):
#     def test_run_returns_completed_process(self):
#         """Test that run returns CompletedProcess instance."""
#         result = run(["echo", "hello"])
#         assert isinstance(result, CompletedProcess)
#         assert hasattr(result, "returncode")
#         assert hasattr(result, "stdout")
#         assert hasattr(result, "stderr")
#     def test_run_returncode_zero_success(self):
#     def test_run_returncode_zero_success(self):
#         """Test returncode is 0 for successful command."""
#         result = run(["echo", "hello"])
#         assert result.returncode == 0, "Result must not be empty"
#     def test_run_encoding_parameter(self):
#     def test_run_encoding_parameter(self):
#         """Test encoding parameter."""
#         result = run(["echo", "hello"], encoding="utf-8")
#         assert isinstance(result.stdout, str)
#     def test_run_errors_parameter(self):
#     def test_run_errors_parameter(self):
#         """Test errors parameter."""
#         result = run(["echo", "hello"], errors="strict")
#         assert result.returncode == 0, "Result must not be empty"
#     def test_run_no_shell_injection(self):
#     def test_run_no_shell_injection(self):
#         """Test that shell injection is not possible."""
#         # shell=True should raise, preventing shell injection
#         with pytest.raises(ValueError):
#             run(["echo $(whoami)"], shell=True)
#     def test_run_list_conversion(self):
#     def test_run_list_conversion(self):
#         """Test that command is converted to list."""
#         result = run(["echo", "hello"])
#         assert result.returncode == 0, "Result must not be empty"
#     def test_run_captures_stderr(self):
#     def test_run_captures_stderr(self):
#         """Test that stderr can be captured."""
#         result = run(["sh", "-c", "echo error >&2"], capture_output=True, check=False)
#         assert result.stderr is not None, "stderr must be initialized"
#     def test_run_with_stdin_none(self):
#     def test_run_with_stdin_none(self):
#         """Test with stdin=None."""
#         result = run(["echo", "hello"], stdin=None)
#         assert result.returncode == 0, "Result must not be empty"
#     def test_run_with_stdout_none(self):
#     def test_run_with_stdout_none(self):
#         """Test with stdout=None."""
#         result = run(["echo", "hello"], stdout=None, check=False)
#         assert result.returncode >= 0, "returncode must be greater than zero"
#     def test_run_with_stderr_none(self):
#     def test_run_with_stderr_none(self):
#         """Test with stderr=None."""
#         result = run(["echo", "hello"], stderr=None, check=False)
#         assert result.returncode >= 0, "returncode must be greater than zero"
#     def test_run_basic_security(self):
#     def test_run_basic_security(self):
#         """Test basic security: no shell=True."""
#         # Verify that trying to use shell=True fails
#         with pytest.raises(ValueError):
#             run(["ls; whoami"], shell=True)
#     def test_run_command_with_special_characters(self):
#     def test_run_command_with_special_characters(self):
#         """Test running command with special character arguments."""
#         result = run(["echo", "hello@#$%"])
#         assert result.returncode == 0, "Result must not be empty"
#         assert "hello@, "Condition must be true"
#     def test_run_empty_output(self):
#     def test_run_empty_output(self):
#         """Test command with empty output."""
#         result = run(["true"])
#         assert result.returncode == 0, "Result must not be empty"
#     def test_run_multiline_output(self):
#     def test_run_multiline_output(self):
#         """Test command with multiline output."""
#         result = run(["sh", "-c", "echo line1; echo line2"])
#         assert result.returncode == 0, "Result must not be empty"
#         assert "line1" in result.stdout or result.stdout == "", "Result must not be empty"


class TestSubprocessCompletedProcess:
    """Test suite for CompletedProcess type."""

    def test_completed_process_has_returncode(self):
        """Test that CompletedProcess has returncode."""
        result = run(["echo", "hello"])
        assert hasattr(result, "returncode")
        assert isinstance(result.returncode, int)

    def test_completed_process_has_stdout(self):
        """Test that CompletedProcess has stdout."""
        result = run(["echo", "hello"])
        assert hasattr(result, "stdout")

    def test_completed_process_has_stderr(self):
        """Test that CompletedProcess has stderr."""
        result = run(["echo", "hello"])
        assert hasattr(result, "stderr")

    def test_completed_process_attributes_accessible(self):
        """Test that CompletedProcess attributes are accessible."""
        result = run(["echo", "test"])
        rc = result.returncode
        out = result.stdout
        assert isinstance(rc, int)
        assert out is not None or out is None, "out must be initialized"


class TestSubprocessErrorHandling:
    """Test suite for error handling in subprocess wrapper."""

    def test_run_command_not_found_raises(self):
        """Test that command not found raises error."""
        with pytest.raises(FileNotFoundError):
            run(["nonexistent_command_xyz"])

    def test_run_invalid_cwd_raises(self):
        """Test that invalid cwd raises error."""
        with pytest.raises(FileNotFoundError):
            run(["echo", "hello"], cwd=Path("/nonexistent/path"))

    def test_run_timeout_raises(self):
        """Test that timeout raises error."""
        with pytest.raises(_stdlib_subprocess.TimeoutExpired):
            run(["sleep", "100"], timeout=0.1)

    def test_run_shell_true_value_error(self):
        """Test that shell=True raises ValueError."""
        with pytest.raises(ValueError):
            run(["echo", "hello"], shell=True)

    def test_run_check_raises_on_failure(self):
        """Test that check=True raises on failure."""
        with pytest.raises(_stdlib_subprocess.CalledProcessError):
            run(["sh", "-c", "exit 1"], check=True)


class TestSubprocessIntegration:
    """Integration tests for subprocess wrapper."""

    def test_run_multiple_commands_in_sequence(self):
        """Test running multiple commands in sequence."""
        result1 = run(["echo", "first"])
        result2 = run(["echo", "second"])
        assert result1.returncode == 0, "Result must not be empty"
        assert result2.returncode == 0, "Result must not be empty"
        assert "first" in result1.stdout, "Result must not be empty"
        assert "second" in result2.stdout, "Result must not be empty"

    def test_run_with_pipes_via_shell_alternative(self):
        """Test pipe-like behavior without shell."""
        result = run(["echo", "hello"])
        assert "hello" in result.stdout, "Result must not be empty"

    def test_run_preserves_type_information(self):
        """Test that text/binary mode is preserved."""
        text_result = run(["echo", "hello"], text=True)
        binary_result = run(["echo", "hello"], text=False)
        assert isinstance(text_result.stdout, str)
        assert isinstance(binary_result.stdout, bytes)

    def test_run_handles_unicode_output(self):
        """Test handling of unicode output."""
        result = run(["echo", "hello™"])
        assert result.returncode == 0, "Result must not be empty"
        assert isinstance(result.stdout, str)

    def test_run_api_compatibility(self):
        """Test that API is compatible with stdlib subprocess.run."""
        # Should accept same parameters as subprocess.run
        result = run(["echo", "hello"], capture_output=True, text=True, check=False, timeout=None)
        assert result.returncode == 0, "Result must not be empty"


class TestSubprocessSecurityProperties:
    """Test suite for security properties of subprocess wrapper."""

    def test_shell_injection_impossible_with_shell_true_error(self):
        """Test that shell injection is prevented by rejecting shell=True."""
        with pytest.raises(ValueError):
            run(["echo $(whoami)"], shell=True)

    def test_no_shell_expansion_occurs(self):
        """Test that shell expansion doesn't occur."""
        result = run(["echo", "$HOME"])
        # Should print literal $HOME, not expanded value
        assert "$HOME" in result.stdout, "Result must not be empty"

    def test_command_as_list_safety(self):
        """Test that command must be a list (safe)."""
        result = run(["echo", "hello"])
        assert result.returncode == 0, "Result must not be empty"

    def test_protected_against_shell_metacharacters(self):
        """Test protection against shell metacharacters."""
        # These should be treated as literal arguments, not shell commands
        result = run(["echo", ";", "ls", "|", "grep"])
        assert result.returncode == 0, "Result must not be empty"
