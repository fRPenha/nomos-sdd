"""Regression checks for the local Nomos installation flow docs/assets."""

from __future__ import annotations

from pathlib import Path


def test_local_install_scripts_exist_and_target_specify_cli():
    bash_script = Path("tools/install-nomos-local.sh")
    powershell_script = Path("tools/install-nomos-local.ps1")

    assert bash_script.is_file()
    assert powershell_script.is_file()

    bash_text = bash_script.read_text(encoding="utf-8")
    powershell_text = powershell_script.read_text(encoding="utf-8")

    assert "uv tool install --from" in bash_text
    assert "specify-cli" in bash_text
    assert "uv tool install --from" in powershell_text
    assert "specify-cli" in powershell_text


def test_readme_documents_how_to_use_nomos_in_another_project():
    readme = Path("README.md").read_text(encoding="utf-8")

    assert "Como usar o Nomos em outro projeto" in readme
    assert "uv tool install --from" in readme
    assert "pipx install -e" in readme
    assert "uv run --project" in readme
    assert "specify nomos init" in readme
    assert "specify nomos demand create" in readme


def test_installation_docs_cover_primary_alternative_and_fallback_flows():
    installation = Path("docs/installation.md").read_text(encoding="utf-8")
    local_development = Path("docs/local-development.md").read_text(encoding="utf-8")
    pipx_doc = Path("docs/install/pipx.md").read_text(encoding="utf-8")
    one_time = Path("docs/install/one-time.md").read_text(encoding="utf-8")

    assert "uv tool install --from" in installation
    assert "specify nomos init" in installation
    assert "tools/install-nomos-local.sh" in local_development
    assert "pipx install -e" in pipx_doc
    assert "uv run --project" in one_time
