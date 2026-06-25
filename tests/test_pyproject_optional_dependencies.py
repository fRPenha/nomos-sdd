"""Contract checks for optional dependency groups in pyproject.toml."""

from __future__ import annotations

from pathlib import Path
import tomllib


def test_dev_extra_includes_pytest_tools():
    with Path("pyproject.toml").open("rb") as f:
        data = tomllib.load(f)

    optional = data["project"]["optional-dependencies"]

    assert "dev" in optional
    assert "pytest>=7.0" in optional["dev"]
    assert "pytest-cov>=4.0" in optional["dev"]
