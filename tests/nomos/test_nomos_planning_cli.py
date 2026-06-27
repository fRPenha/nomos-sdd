"""Tests for the Nomos discovery/backlog/planning scaffold."""

from __future__ import annotations

import os
from pathlib import Path

from typer.testing import CliRunner


PLANNING_FILES = [
    ".nomos/discovery/project-snapshot.md",
    ".nomos/discovery/current-architecture.md",
    ".nomos/discovery/target-architecture.md",
    ".nomos/discovery/risks-and-constraints.md",
    ".nomos/discovery/open-questions.md",
    ".nomos/backlog/backlog.md",
    ".nomos/backlog/demand-map.md",
    ".nomos/backlog/dependency-map.md",
    ".nomos/backlog/readiness-criteria.md",
    ".nomos/planning/product-brief.md",
    ".nomos/planning/roadmap.md",
    ".nomos/planning/next-demand.md",
    ".nomos/planning/agent-planning-brief.md",
]


def test_planning_init_requires_nomos_workspace(tmp_path):
    from specify_cli import app

    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / ".git").mkdir()

    old_cwd = os.getcwd()
    try:
        os.chdir(repo)
        result = CliRunner().invoke(
            app,
            ["nomos", "planning", "init"],
            catch_exceptions=False,
        )
    finally:
        os.chdir(old_cwd)

    assert result.exit_code == 1
    assert "specify nomos init" in result.output


def test_planning_init_creates_discovery_backlog_and_planning(tmp_path):
    from specify_cli import app

    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / ".git").mkdir()

    runner = CliRunner()
    old_cwd = os.getcwd()
    try:
        os.chdir(repo)
        init_result = runner.invoke(app, ["nomos", "init"], catch_exceptions=False)
        planning_result = runner.invoke(
            app,
            ["nomos", "planning", "init"],
            catch_exceptions=False,
        )
    finally:
        os.chdir(old_cwd)

    assert init_result.exit_code == 0, init_result.output
    assert planning_result.exit_code == 0, planning_result.output

    assert (repo / ".nomos" / "discovery").is_dir()
    assert (repo / ".nomos" / "backlog").is_dir()
    assert (repo / ".nomos" / "planning").is_dir()

    for relative_path in PLANNING_FILES:
        assert (repo / relative_path).exists(), relative_path


def test_planning_init_force_overwrites_existing_templates(tmp_path):
    from specify_cli import app

    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / ".git").mkdir()

    runner = CliRunner()
    old_cwd = os.getcwd()
    try:
        os.chdir(repo)
        assert runner.invoke(app, ["nomos", "init"], catch_exceptions=False).exit_code == 0
        assert (
            runner.invoke(app, ["nomos", "planning", "init"], catch_exceptions=False).exit_code
            == 0
        )
        target = repo / ".nomos" / "planning" / "product-brief.md"
        target.write_text("conteudo alterado\n", encoding="utf-8")
        no_force = runner.invoke(app, ["nomos", "planning", "init"], catch_exceptions=False)
        after_no_force = target.read_text(encoding="utf-8")
        with_force = runner.invoke(
            app,
            ["nomos", "planning", "init", "--force"],
            catch_exceptions=False,
        )
    finally:
        os.chdir(old_cwd)

    assert no_force.exit_code == 0, no_force.output
    assert after_no_force == "conteudo alterado\n"
    assert with_force.exit_code == 0, with_force.output
    assert target.read_text(encoding="utf-8") != "conteudo alterado\n"


def test_planning_status_reports_missing_and_present_artifacts(tmp_path):
    from specify_cli import app

    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / ".git").mkdir()

    runner = CliRunner()
    old_cwd = os.getcwd()
    try:
        os.chdir(repo)
        assert runner.invoke(app, ["nomos", "init"], catch_exceptions=False).exit_code == 0
        before = runner.invoke(
            app,
            ["nomos", "planning", "status"],
            catch_exceptions=False,
        )
        assert (
            runner.invoke(app, ["nomos", "planning", "init"], catch_exceptions=False).exit_code
            == 0
        )
        after = runner.invoke(
            app,
            ["nomos", "planning", "status"],
            catch_exceptions=False,
        )
    finally:
        os.chdir(old_cwd)

    assert before.exit_code == 0, before.output
    assert "Discovery" in before.output
    assert "Backlog" in before.output
    assert "Planning" in before.output
    assert "Ausentes" in before.output
    assert "agent-planning-brief.md" in before.output
    assert "next-demand.md" in before.output

    assert after.exit_code == 0, after.output
    assert "Presentes" in after.output
    assert "Próximo passo sugerido" in after.output
    assert "agent-planning-brief.md" in after.output
    assert "next-demand.md" in after.output


def test_readme_documents_discovery_backlog_planning_flow():
    readme = Path("README.md").read_text(encoding="utf-8")

    assert "Discovery" in readme
    assert "Backlog" in readme
    assert "Planning" in readme
    assert "specify nomos planning init" in readme
    assert "specify nomos planning status" in readme
    assert ".nomos/planning/agent-planning-brief.md" not in readme or "agent-planning-brief.md" in readme
