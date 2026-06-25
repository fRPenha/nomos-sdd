# Installation Guide

## Prerequisites

- **Linux/macOS** (or Windows; PowerShell scripts now supported without WSL)
- AI coding agent: [Claude Code](https://www.anthropic.com/claude-code), [GitHub Copilot](https://code.visualstudio.com/), [Codebuddy CLI](https://www.codebuddy.ai/cli), [Gemini CLI](https://github.com/google-gemini/gemini-cli), or [Pi Coding Agent](https://pi.dev)
- [uv](https://docs.astral.sh/uv/) for package management (recommended) or [pipx](https://pipx.pypa.io/) for persistent installation
- [Python 3.11+](https://www.python.org/downloads/)
- [Git](https://git-scm.com/downloads) _(optional — required only when the git extension is enabled)_

## Installation

> [!IMPORTANT]
> The only official, maintained packages for Spec Kit come from the [github/spec-kit](https://github.com/github/spec-kit) GitHub repository. Any packages with the same name available on PyPI (e.g. `specify-cli` on pypi.org) are **not** affiliated with this project and are not maintained by the Spec Kit maintainers. For normal installs, use the GitHub-based commands shown below. For offline or air-gapped environments, locally built wheels created from this repository are also valid.

## Local Nomos From a Checkout

If you are working with this Nomos fork directly and want to use `specify nomos ...` in other repositories without activating the checkout's `.venv`, install the tool from your local clone.

### Primary Flow: `uv tool install --from`

From the local checkout:

```bash
./tools/install-nomos-local.sh
```

Or run the underlying command directly:

```bash
uv tool install --from /path/to/nomos-sdd specify-cli
```

After installation, go to any other Git repository and run:

```bash
specify nomos init
specify nomos demand create my-demand
```

### Fallback Without Persistent Install

If `uv` is available but you do not want a persistent install yet, use:

```bash
uv run --project /path/to/nomos-sdd specify nomos init
uv run --project /path/to/nomos-sdd specify nomos demand create my-demand
```

This is the fallback path, not the recommended daily workflow.

### Persistent Installation (Recommended)

Install once and use everywhere. Replace `vX.Y.Z` with a tag from [Releases](https://github.com/github/spec-kit/releases):

> [!NOTE]
> The command below requires **[uv](https://docs.astral.sh/uv/)**. If you see `command not found: uv`, [install uv first](./install/uv.md).

```bash
uv tool install specify-cli --from git+https://github.com/github/spec-kit.git@vX.Y.Z
```

Then initialize a project:

```bash
specify init <PROJECT_NAME> --integration copilot
```

### One-time Usage

Run directly without installing — see the [One-time usage (uvx)](install/one-time.md) guide.

### Alternative Package Managers

- **pipx** — see the [pipx installation guide](install/pipx.md)
- **Enterprise / Air-Gapped** — see the [air-gapped installation guide](install/air-gapped.md)

### Specify Integration

Interactive terminals prompt you to choose a coding agent integration during initialization. Non-interactive sessions, such as CI or piped runs, default to GitHub Copilot unless you pass `--integration`.

You can proactively specify your coding agent integration during initialization:

```bash
specify init <project_name> --integration claude
specify init <project_name> --integration gemini
specify init <project_name> --integration copilot
specify init <project_name> --integration codebuddy
specify init <project_name> --integration pi
```

### Specify Script Type (Shell vs PowerShell)

All automation scripts now have both Bash (`.sh`) and PowerShell (`.ps1`) variants.

Auto behavior:

- Windows default: `ps`
- Other OS default: `sh`
- Interactive mode: you'll be prompted unless you pass `--script`

Force a specific script type:

```bash
specify init <project_name> --script sh
specify init <project_name> --script ps
```

### Ignore Agent Tools Check

If you prefer to get the templates without checking for the right tools:

```bash
specify init <project_name> --integration claude --ignore-agent-tools
```

## Verification

After installation, run the following command to confirm the correct version is installed:

```bash
specify version
```

This helps verify you are running the official Spec Kit build from GitHub, not an unrelated package with the same name.

**Stay current:** Run `specify self check` periodically to learn whether a newer release is available — it is read-only and never modifies your installation. When you are ready to upgrade, follow the [Upgrade Guide](./upgrade.md).

After initialization, you should see the following commands available in your coding agent:

- `/speckit.specify` - Create specifications
- `/speckit.plan` - Generate implementation plans  
- `/speckit.tasks` - Break down into actionable tasks

Scripts are installed into a variant subdirectory matching the chosen script type:

- `.specify/scripts/bash/` — contains `.sh` scripts (default on Linux/macOS)
- `.specify/scripts/powershell/` — contains `.ps1` scripts (default on Windows)

## Troubleshooting

### Enterprise / Air-Gapped Installation

If your environment blocks access to PyPI or GitHub, see the [Enterprise / Air-Gapped Installation](install/air-gapped.md) guide for step-by-step instructions on creating portable wheel bundles.

### Git Credential Manager on Linux

If you're having issues with Git authentication on Linux, see the [Air-Gapped Installation guide](install/air-gapped.md#git-credential-manager-on-linux) for Git Credential Manager setup instructions.
