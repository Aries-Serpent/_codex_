from mcp.packager.config import PackageConfig


def test_package_config_defaults():
    config = PackageConfig(name="my_pkg")
    assert config.name == "my_pkg"
    assert config.description == ""
    assert config.template == "base"
    assert config.output_dir == "./mcp_package"
    assert config.python_package == "mcp_package"
    assert config.entrypoint == "app.py"
    assert config.include_cli is True
    assert config.include_tests is True
    assert config.include_docs is True
    assert config.include_serverless is False
    assert config.serverless_target is None
    assert config.dependencies == []
    assert config.env == {}
    assert config.features == []


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
    assert config.description == "desc"
    assert config.template == "custom"
    assert config.output_dir == "./out"
    assert config.python_package == "custom_pkg"
    assert config.entrypoint == "main.py"
    assert config.include_cli is False
    assert config.include_tests is False
    assert config.include_docs is False
    assert config.include_serverless is True
    assert config.serverless_target == "aws"
    assert config.dependencies == ["requests"]
    assert config.env == {"ENV": "prod"}
    assert config.features == ["auth"]
