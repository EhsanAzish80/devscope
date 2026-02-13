"""Tests for devscope CLI."""

from pathlib import Path
from tempfile import TemporaryDirectory

from click.testing import CliRunner

from devscope.cli import cli


class TestCLI:
    """Test the CLI interface."""

    def test_cli_help(self) -> None:
        """Test that help command works."""
        runner = CliRunner()
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "devscope" in result.output

    def test_scan_help(self) -> None:
        """Test scan command help."""
        runner = CliRunner()
        result = runner.invoke(cli, ["scan", "--help"])
        assert result.exit_code == 0
        assert "scan" in result.output.lower()

    def test_scan_current_directory(self) -> None:
        """Test scanning current directory."""
        runner = CliRunner()
        with TemporaryDirectory() as tmpdir:
            # Create some test files
            root = Path(tmpdir)
            (root / "test.py").write_text("print('hello')\\n")
            (root / "test.js").write_text("console.log('hello');\\n")

            result = runner.invoke(cli, ["scan", tmpdir])

            # Check that it completed successfully
            if result.exit_code != 0:
                print(f"\\nOutput:\\n{result.output}")
                if result.exception:
                    import traceback

                    print(
                        f"\\nException:\\n{''.join(traceback.format_exception(type(result.exception), result.exception, result.exception.__traceback__))}"
                    )
            assert result.exit_code == 0
            assert "Analysis complete" in result.output or "✓" in result.output

    def test_scan_with_path(self) -> None:
        """Test scanning a specific path."""
        runner = CliRunner()
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "main.py").write_text("# test file\n")

            result = runner.invoke(cli, ["scan", str(root)])
            assert result.exit_code == 0

    def test_version(self) -> None:
        """Test version option."""
        runner = CliRunner()
        result = runner.invoke(cli, ["--version"])
        assert result.exit_code == 0
        assert "0.1.0" in result.output
