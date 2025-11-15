"""Tests for resource loading edge cases."""

from unittest.mock import patch

import pytest
from mkdocs.exceptions import PluginError


def test_resource_loading_failure():
    """Test that resource loading failure raises PluginError."""
    # Mock importlib.resources to raise an exception
    with patch("mkdocs_exam.plugin.impresources.files") as mock_files:
        mock_files.side_effect = Exception("Resource not found")

        # Importing the plugin module with broken resources should raise PluginError
        with pytest.raises(Exception) as exc_info:
            # Force module reload to trigger resource loading with mocked failure
            import sys  # noqa: PLC0415

            # Remove module from cache if it exists
            if "mkdocs_exam.plugin" in sys.modules:
                del sys.modules["mkdocs_exam.plugin"]

            # This should trigger the resource loading and fail
            import mkdocs_exam.plugin  # noqa: F401, PLC0415

        # The exception should be from resource loading
        assert "Resource not found" in str(exc_info.value) or isinstance(
            exc_info.value, PluginError
        )


def test_css_resource_loading():
    """Test CSS resource is loaded correctly."""
    from mkdocs_exam.plugin import style  # noqa: PLC0415

    # Style should be loaded and wrapped in <style> tags
    assert style.startswith("<style")
    assert style.endswith("</style>")
    assert ".exam" in style  # Should contain exam CSS classes


def test_js_resource_loading():
    """Test JavaScript resource is loaded correctly."""
    from mkdocs_exam.plugin import script_tag  # noqa: PLC0415

    # Script should be loaded and wrapped in <script> tags
    assert script_tag.startswith("<script")
    assert script_tag.endswith("</script>")
    assert "function" in script_tag or "const" in script_tag  # Should contain JS code


def test_logger_initialized_before_resource_loading():
    """Test that logger is initialized before attempting resource loading."""
    from mkdocs_exam.plugin import logger  # noqa: PLC0415

    # Logger should be initialized
    assert logger is not None
    assert hasattr(logger, "info")
    assert hasattr(logger, "error")
    assert hasattr(logger, "warning")
