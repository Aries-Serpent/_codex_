from unittest.mock import MagicMock, patch

from mcp.packager.cli import main


@patch("mcp.packager.cli.argparse.ArgumentParser.parse_args")
@patch("mcp.packager.cli.load_config")
@patch("mcp.packager.cli.generate_package")
@patch("builtins.print")
def test_main(mock_print, mock_generate, mock_load, mock_parse):
    args = MagicMock()
    args.config = "config.yaml"
    args.output = "out_dir"
    mock_parse.return_value = args

    mock_config = MagicMock()
    mock_load.return_value = mock_config
    mock_generate.return_value = "out_dir/pkg"

    main()

    mock_parse.assert_called_once()
    mock_load.assert_called_once_with("config.yaml")
    mock_generate.assert_called_once_with(mock_config, output_dir="out_dir")
    mock_print.assert_called_once_with("Generated MCP package at out_dir/pkg")
