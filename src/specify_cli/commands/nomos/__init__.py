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

planning_app = typer.Typer(
    name="planning",
    help="Manage Nomos discovery/backlog/planning artifacts",
    add_completion=False,
)

demand_app = typer.Typer(
    name="demand",
    help="Manage Nomos demand workspaces",
    add_completion=False,
)
nomos_app.add_typer(planning_app, name="planning")
nomos_app.add_typer(demand_app, name="demand")

_DEMAND_ID_RE = re.compile(r"^[a-z0-9](?:[a-z0-9-]*[a-z0-9])?$")
_DEFAULT_PROFILE = "generic"
_PLANNING_FILE_MAP = {
    "discovery/project-snapshot.md": "discovery/project-snapshot.md",
    "discovery/current-architecture.md": "discovery/current-architecture.md",
    "discovery/target-architecture.md": "discovery/target-architecture.md",
    "discovery/risks-and-constraints.md": "discovery/risks-and-constraints.md",
    "discovery/open-questions.md": "discovery/open-questions.md",
    "backlog/backlog.md": "backlog/backlog.md",
    "backlog/demand-map.md": "backlog/demand-map.md",
    "backlog/dependency-map.md": "backlog/dependency-map.md",
    "backlog/readiness-criteria.md": "backlog/readiness-criteria.md",
    "planning/product-brief.md": "planning/product-brief.md",
    "planning/roadmap.md": "planning/roadmap.md",
    "planning/next-demand.md": "planning/next-demand.md",
    "planning/agent-planning-brief.md": "planning/agent-planning-brief.md",
}


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


def _require_nomos_workspace(repo_root: Path) -> Path:
    nomos_root = _nomos_root(repo_root)
    if not (nomos_root / "project").is_dir():
        _fail("Nomos is not initialized in this repository. Run 'specify nomos init' first.")
    return nomos_root


def _initialize_planning_files(repo_root: Path, *, force: bool) -> Path:
    templates_dir = _require_nomos_templates_dir()
    nomos_root = _require_nomos_workspace(repo_root)

    for relative_dir in (
        Path("discovery"),
        Path("backlog"),
        Path("planning"),
    ):
        (nomos_root / relative_dir).mkdir(parents=True, exist_ok=True)

    replacements = _project_replacements(repo_root, _load_profile(repo_root))
    for template_name, destination in _PLANNING_FILE_MAP.items():
        content = _render_template(templates_dir / template_name, replacements)
        _write_text_file(nomos_root / destination, content, force=force)

    return nomos_root


def _relative_nomos_paths() -> list[str]:
    return [f".nomos/{destination}" for destination in _PLANNING_FILE_MAP.values()]


def _file_state_label(path: Path) -> str:
    if not path.exists():
        return "ausente"
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return "presente"
    return "presente (vazio)" if text.strip() == "" else "presente"


def _initialize_demand_files(
    repo_root: Path,
    demand_id: str,
    title: str | None,
    *,
    force: bool,
) -> Path:
    if not _DEMAND_ID_RE.match(demand_id):
        _fail("Demand id must be kebab-case using lowercase letters, numbers, and hyphens.")

    nomos_root = _require_nomos_workspace(repo_root)

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


@planning_app.command("init")
def planning_init(
    force: bool = typer.Option(
        False,
        "--force",
        help="Overwrite existing discovery/backlog/planning templates inside .nomos/",
    ),
) -> None:
    """Initialize Nomos discovery, backlog, and planning artifacts."""
    repo_root = _require_repo_root()
    nomos_root = _initialize_planning_files(repo_root, force=force)

    console.print(
        f"[green]✓[/green] Planning workspace ready at [cyan]{nomos_root}[/cyan]"
    )
    console.print(
        "[dim]Discovery, backlog, and planning artifacts are ready for an agent to structure the project before creating a specific demand.[/dim]"
    )


@planning_app.command("status")
def planning_status() -> None:
    """Show Nomos discovery/backlog/planning scaffold status."""
    repo_root = _require_repo_root()
    nomos_root = _nomos_root(repo_root)

    if not nomos_root.exists():
        console.print("[yellow]Nomos workspace:[/yellow] ausente")
        console.print("Próximo passo sugerido: execute [cyan]specify nomos init[/cyan].")
        return

    console.print(f"[cyan]Workspace:[/cyan] {nomos_root}")
    console.print(
        f"[cyan].nomos existe:[/cyan] {'sim' if nomos_root.exists() else 'não'}"
    )

    discovery_dir = nomos_root / "discovery"
    backlog_dir = nomos_root / "backlog"
    planning_dir = nomos_root / "planning"
    console.print(f"[cyan]Discovery:[/cyan] {'presente' if discovery_dir.is_dir() else 'ausente'}")
    console.print(f"[cyan]Backlog:[/cyan] {'presente' if backlog_dir.is_dir() else 'ausente'}")
    console.print(f"[cyan]Planning:[/cyan] {'presente' if planning_dir.is_dir() else 'ausente'}")

    present: list[str] = []
    missing: list[str] = []
    for relative_path in _relative_nomos_paths():
        target = repo_root / relative_path
        if target.exists():
            present.append(relative_path)
        else:
            missing.append(relative_path)

    console.print("\n[bold]Presentes[/bold]")
    if present:
        for relative_path in present:
            console.print(
                f"- {relative_path} — {_file_state_label(repo_root / relative_path)}"
            )
    else:
        console.print("- nenhum artefato encontrado")

    console.print("\n[bold]Ausentes[/bold]")
    if missing:
        for relative_path in missing:
            console.print(f"- {relative_path}")
    else:
        console.print("- nenhum")

    agent_brief = nomos_root / "planning" / "agent-planning-brief.md"
    next_demand = nomos_root / "planning" / "next-demand.md"
    console.print(
        f"\n[cyan]planning/agent-planning-brief.md:[/cyan] {_file_state_label(agent_brief)}"
    )
    console.print(
        f"[cyan]planning/next-demand.md:[/cyan] {_file_state_label(next_demand)}"
    )

    if not (nomos_root / "project").is_dir():
        next_step = "execute specify nomos init"
    elif missing:
        next_step = "execute specify nomos planning init"
    else:
        next_step = (
            "preencha discovery/, backlog/ e planning/, depois use planning/next-demand.md para decidir qual demanda criar"
        )

    console.print(f"\n[bold]Próximo passo sugerido[/bold]")
    console.print(f"- {next_step}")


def register(app: typer.Typer) -> None:
    """Register the ``specify nomos`` command group."""
    app.add_typer(nomos_app, name="nomos")
