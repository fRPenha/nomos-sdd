"""``specify nomos`` command group — local project-scoped Nomos workspace."""

from __future__ import annotations

import json
import re
from datetime import date
from pathlib import Path

import typer

from ..._assets import _locate_bundled_nomos_templates
from ..._console import console

nomos_app = typer.Typer(
    name="nomos",
    help="Manage the local .nomos workspace inside a repository",
    add_completion=False,
)

demand_app = typer.Typer(
    name="demand",
    help="Manage Nomos demand workspaces",
    add_completion=False,
)
nomos_app.add_typer(demand_app, name="demand")

_DEMAND_ID_RE = re.compile(r"^[a-z0-9](?:[a-z0-9-]*[a-z0-9])?$")
_DEFAULT_PROFILE = "generic"


def _fail(message: str) -> None:
    console.print(f"[red]Error:[/red] {message}")
    raise typer.Exit(1)


def _find_repo_root(start: Path) -> Path | None:
    """Return the nearest ancestor that looks like a git repository root."""
    current = start.resolve()
    for candidate in (current, *current.parents):
        git_marker = candidate / ".git"
        if git_marker.exists():
            return candidate
    return None


def _require_repo_root() -> Path:
    repo_root = _find_repo_root(Path.cwd())
    if repo_root is None:
        _fail("Not inside a git repository. Run this command from a repository worktree.")
    return repo_root


def _require_nomos_templates_dir() -> Path:
    templates_dir = _locate_bundled_nomos_templates()
    if templates_dir is None:
        _fail("Nomos templates are not available in this installation.")
    return templates_dir


def _nomos_root(repo_root: Path) -> Path:
    return repo_root / ".nomos"


def _render_template(template_path: Path, replacements: dict[str, str]) -> str:
    content = template_path.read_text(encoding="utf-8")
    for key, value in replacements.items():
        content = content.replace(f"__{key}__", value)
    return content


def _write_text_file(path: Path, content: str, *, force: bool) -> None:
    if path.exists() and not force:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _ensure_gitignore_rule(repo_root: Path, rule: str) -> None:
    gitignore_path = repo_root / ".gitignore"
    if gitignore_path.exists():
        current = gitignore_path.read_text(encoding="utf-8")
        existing_rules = {line.strip() for line in current.splitlines()}
        if rule in existing_rules or f"/{rule}" in existing_rules:
            return
        prefix = "" if current.endswith("\n") or current == "" else "\n"
        gitignore_path.write_text(
            f"{current}{prefix}{rule}\n",
            encoding="utf-8",
        )
        return

    gitignore_path.write_text(f"{rule}\n", encoding="utf-8")


def _load_profile(repo_root: Path) -> str:
    profile_path = _nomos_root(repo_root) / "project" / "profile.json"
    if not profile_path.exists():
        return _DEFAULT_PROFILE
    try:
        raw = json.loads(profile_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return _DEFAULT_PROFILE
    profile = raw.get("profile")
    return profile if isinstance(profile, str) and profile else _DEFAULT_PROFILE


def _project_replacements(repo_root: Path, profile: str) -> dict[str, str]:
    return {
        "DATE": date.today().isoformat(),
        "PROFILE": profile,
        "PROJECT_NAME": repo_root.name,
    }


def _demand_replacements(repo_root: Path, demand_id: str, title: str | None) -> dict[str, str]:
    demand_title = title.strip() if isinstance(title, str) and title.strip() else demand_id.replace("-", " ").title()
    return {
        "DATE": date.today().isoformat(),
        "DEMAND_ID": demand_id,
        "DEMAND_TITLE": demand_title,
        "PROFILE": _load_profile(repo_root),
        "PROJECT_NAME": repo_root.name,
    }


def _initialize_project_files(repo_root: Path, profile: str, *, force: bool) -> None:
    templates_dir = _require_nomos_templates_dir()
    root = _nomos_root(repo_root)

    for relative_dir in (
        Path("project"),
        Path("demands"),
        Path("exports"),
        Path("private"),
        Path("cache"),
    ):
        (root / relative_dir).mkdir(parents=True, exist_ok=True)

    replacements = _project_replacements(repo_root, profile)
    file_map = {
        "project/project.json": "project/project.json",
        "project/profile.json": "project/profile.json",
        "project/glossary.md": "project/glossary.md",
        "project/conventions.md": "project/conventions.md",
        "project/architecture-notes.md": "project/architecture-notes.md",
        "current": "current",
    }
    for template_name, destination in file_map.items():
        content = _render_template(templates_dir / template_name, replacements)
        _write_text_file(root / destination, content, force=force)


def _initialize_demand_files(
    repo_root: Path,
    demand_id: str,
    title: str | None,
    *,
    force: bool,
) -> Path:
    if not _DEMAND_ID_RE.match(demand_id):
        _fail("Demand id must be kebab-case using lowercase letters, numbers, and hyphens.")

    nomos_root = _nomos_root(repo_root)
    if not (nomos_root / "project").is_dir():
        _fail("Nomos is not initialized in this repository. Run 'specify nomos init' first.")

    demand_dir = nomos_root / "demands" / demand_id
    if demand_dir.exists() and not force:
        _fail(f"Demand '{demand_id}' already exists. Re-run with --force to overwrite files.")

    templates_dir = _require_nomos_templates_dir()
    replacements = _demand_replacements(repo_root, demand_id, title)
    file_map = {
        "demands/demand.json": "demand.json",
        "demands/interview.md": "interview.md",
        "demands/discovery.md": "discovery.md",
        "demands/impact-analysis.md": "impact-analysis.md",
        "demands/functional-spec.md": "functional-spec.md",
        "demands/technical-spec.md": "technical-spec.md",
        "demands/business-rules.md": "business-rules.md",
        "demands/acceptance-criteria.md": "acceptance-criteria.md",
        "demands/constraints.md": "constraints.md",
        "demands/decisions.md": "decisions.md",
        "demands/implementation-plan.md": "implementation-plan.md",
        "demands/tasks.md": "tasks.md",
        "demands/agent-package.md": "agent-package.md",
        "demands/contracts/README.md": "contracts/README.md",
        "demands/prompts/README.md": "prompts/README.md",
    }
    for template_name, destination in file_map.items():
        content = _render_template(templates_dir / template_name, replacements)
        _write_text_file(demand_dir / destination, content, force=force)

    _write_text_file(nomos_root / "current", f"{demand_id}\n", force=True)
    return demand_dir


@nomos_app.command("init")
def nomos_init(
    profile: str = typer.Option(
        _DEFAULT_PROFILE,
        "--profile",
        help="Initial Nomos project profile to record in .nomos/project/profile.json",
    ),
    force: bool = typer.Option(
        False,
        "--force",
        help="Overwrite existing Nomos scaffold files inside .nomos/",
    ),
) -> None:
    """Initialize a local .nomos workspace inside the current repository."""
    repo_root = _require_repo_root()
    _initialize_project_files(repo_root, profile, force=force)
    _ensure_gitignore_rule(repo_root, ".nomos/")

    console.print(f"[green]✓[/green] Nomos workspace ready at [cyan]{repo_root / '.nomos'}[/cyan]")
    console.print("[dim]Demand artifacts remain local until you choose to export or version them.[/dim]")


@demand_app.command("create")
def demand_create(
    demand_id: str = typer.Argument(..., help="Kebab-case demand identifier"),
    title: str = typer.Option(
        "",
        "--title",
        help="Optional human-readable demand title used inside generated artifacts",
    ),
    force: bool = typer.Option(
        False,
        "--force",
        help="Overwrite files for an existing demand directory",
    ),
) -> None:
    """Create a new demand workspace in .nomos/demands/<demand-id>/."""
    repo_root = _require_repo_root()
    demand_dir = _initialize_demand_files(repo_root, demand_id, title, force=force)

    console.print(f"[green]✓[/green] Demand workspace created at [cyan]{demand_dir}[/cyan]")
    console.print(
        "[dim]Use agent-package.md as the primary handoff file for Codex, Claude Code, Gemini CLI, or another implementation agent.[/dim]"
    )


def register(app: typer.Typer) -> None:
    """Register the ``specify nomos`` command group."""
    app.add_typer(nomos_app, name="nomos")
