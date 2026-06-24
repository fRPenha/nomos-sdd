"""Tests for the minimal `specify nomos` workflow."""

from __future__ import annotations

import json
import os

from typer.testing import CliRunner


def test_nomos_init_creates_local_workspace_and_gitignore(tmp_path):
    from specify_cli import app

    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / ".git").mkdir()

    old_cwd = os.getcwd()
    try:
        os.chdir(repo)
        result = CliRunner().invoke(app, ["nomos", "init"], catch_exceptions=False)
    finally:
        os.chdir(old_cwd)

    assert result.exit_code == 0, result.output
    assert (repo / ".nomos" / "project" / "project.json").exists()
    assert (repo / ".nomos" / "project" / "profile.json").exists()
    assert (repo / ".nomos" / "project" / "glossary.md").exists()
    assert (repo / ".nomos" / "demands").is_dir()
    assert (repo / ".nomos" / "exports").is_dir()
    assert (repo / ".nomos" / "private").is_dir()
    assert (repo / ".nomos" / "cache").is_dir()
    assert (repo / ".nomos" / "current").exists()

    project_data = json.loads(
        (repo / ".nomos" / "project" / "project.json").read_text(encoding="utf-8")
    )
    assert project_data["project_name"] == "repo"
    assert project_data["workspace_root"] == ".nomos"

    gitignore_lines = (repo / ".gitignore").read_text(encoding="utf-8").splitlines()
    assert ".nomos/" in gitignore_lines


def test_nomos_demand_create_scaffolds_demand_and_updates_current(tmp_path):
    from specify_cli import app

    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / ".git").mkdir()
    (repo / "src").mkdir()

    runner = CliRunner()
    old_cwd = os.getcwd()
    try:
        os.chdir(repo)
        init_result = runner.invoke(
            app,
            ["nomos", "init", "--profile", "advpl"],
            catch_exceptions=False,
        )
        os.chdir(repo / "src")
        demand_result = runner.invoke(
            app,
            ["nomos", "demand", "create", "nova-funcionalidade", "--title", "Nova Funcionalidade"],
            catch_exceptions=False,
        )
    finally:
        os.chdir(old_cwd)

    assert init_result.exit_code == 0, init_result.output
    assert demand_result.exit_code == 0, demand_result.output

    demand_dir = repo / ".nomos" / "demands" / "nova-funcionalidade"
    assert (demand_dir / "demand.json").exists()
    assert (demand_dir / "functional-spec.md").exists()
    assert (demand_dir / "technical-spec.md").exists()
    assert (demand_dir / "impact-analysis.md").exists()
    assert (demand_dir / "implementation-plan.md").exists()
    assert (demand_dir / "tasks.md").exists()
    assert (demand_dir / "agent-package.md").exists()
    assert (demand_dir / "contracts" / "README.md").exists()
    assert (demand_dir / "prompts" / "README.md").exists()

    demand_data = json.loads((demand_dir / "demand.json").read_text(encoding="utf-8"))
    assert demand_data["id"] == "nova-funcionalidade"
    assert demand_data["profile"] == "advpl"

    current = (repo / ".nomos" / "current").read_text(encoding="utf-8").strip()
    assert current == "nova-funcionalidade"

    package = (demand_dir / "agent-package.md").read_text(encoding="utf-8")
    assert "functional-spec.md" in package
    assert ".nomos/demands/nova-funcionalidade/" in package
