# @pytest.mark.skipif(sys.version_info < (3, 12), reason="Python 3.12+ specific tests")
class TestPython312TomlFeatures:
    """Test Python 3.12-specific TOML features."""

    def test_tomllib_load_performance(self, tmp_path):
        """
        Test tomllib performance in Python 3.12.

        Python 3.12 has optimized tomllib implementation.
        """
        import time

        # Create a moderately sized TOML file
        toml_file = tmp_path / "large.toml"
        sections = []
        for i in range(100):
            sections.append(f"""
[section_{i}]
key1 = "value1"
key2 = "value2"
key3 = 123
key4 = true
""")
        toml_file.write_text("\n".join(sections))

        try:
            import tomllib
        except ImportError:
            pytest.skip("tomllib not available")
        else:
            start = time.time()
            with open(toml_file, "rb") as f:
                data = tomllib.load(f)
            elapsed = time.time() - start

            assert len(data) == 100, "Data must not be empty"
            assert elapsed < 1.0, "elapsed is not valid"

    def test_unicode_handling(self, tmp_path):
        """Test Unicode handling in TOML files."""
        toml_file = tmp_path / "unicode.toml"
        toml_content = """
[project]
name = "测试项目"
description = "Test with émojis 🚀 and ümlauts"
author = "José García"
"""
        toml_file.write_text(toml_content, encoding="utf-8")

        data: dict = {}
        try:
            import tomllib

            with open(toml_file, "rb") as f:
                data = tomllib.load(f)
        except ImportError:
            pytest.skip("tomllib not available")

        assert data["project"]["name"] == "测试项目", "Data must not be empty"
        assert "🚀" in data["project"]["description"], "Data must not be empty"
        assert data["project"]["author"] == "José García", "Data must not be empty"


class TestTomlErrorHandling:
    """Test TOML error handling."""

    def test_invalid_toml_syntax(self, tmp_path):
        """Test handling of invalid TOML syntax."""
        toml_file = tmp_path / "invalid.toml"
        toml_file.write_text("this is not valid TOML syntax [[")

        try:
            import tomllib

            with pytest.raises(tomllib.TOMLDecodeError), open(toml_file, "rb") as f:
                tomllib.load(f)
        except ImportError:
            try:
                import tomli

                with pytest.raises(tomli.TOMLDecodeError):
                    with open(toml_file, "rb") as f:
                        tomli.load(f)
            except ImportError:
                pytest.skip("Neither tomllib nor tomli available")

    def test_missing_file(self):
        """Test handling of missing TOML file."""
        try:
            import tomllib

            with pytest.raises(FileNotFoundError), open("nonexistent.toml", "rb") as f:
                tomllib.load(f)
        except ImportError:
            pytest.skip("tomllib not available")
