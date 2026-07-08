from mcp.packager.config import PackageConfig


def test_package_config_defaults():
    config = PackageConfig(name="my_pkg")
    assert config.name == "my_pkg", "name is not valid"
    assert config.description == "", "description is not valid"
    assert config.template == "base", "template is not valid"
    assert config.output_dir == "./mcp_package", "output_dir is not valid"
    assert config.python_package == "mcp_package", "python_package is not valid"
    assert config.entrypoint == "app.py", "entrypoint is not valid"
    assert config.include_cli is True, "include_cli is not valid"
    assert config.include_tests is True, "include_tests is not valid"
    assert config.include_docs is True, "include_docs is not valid"
    assert config.include_serverless is False, "include_serverless is not valid"
    assert config.serverless_target is None, "serverless_target is not valid"
    assert config.dependencies == [], "dependencies is not valid"
    assert config.env == {}, "env is not valid"
    assert config.features == [], "features is not valid"


def test_package_config_custom():
    config = PackageConfig(
        name="my_pkg",
        description="desc",
        template="custom",
        output_dir="./out",
        python_package="custom_pkg",
        entrypoint="main.py",
        include_cli=False,
        include_tests=False,
        include_docs=False,
        include_serverless=True,
        serverless_target="aws",
        dependencies=["requests"],
        env={"ENV": "prod"},
        features=["auth"],
    )
    assert config.description == "desc", "description is not valid"
    assert config.template == "custom", "template is not valid"
    assert config.output_dir == "./out", "output_dir is not valid"
    assert config.python_package == "custom_pkg", "python_package is not valid"
    assert config.entrypoint == "main.py", "entrypoint is not valid"
    assert config.include_cli is False, "include_cli is not valid"
    assert config.include_tests is False, "include_tests is not valid"
    assert config.include_docs is False, "include_docs is not valid"
    assert config.include_serverless is True, "include_serverless is not valid"
    assert config.serverless_target == "aws", "serverless_target is not valid"
    assert config.dependencies == ["requests"], "dependencies is not valid"
    assert config.env == {"ENV": "prod"}, "env is not valid"
    assert config.features == ["auth"], "features is not valid"
