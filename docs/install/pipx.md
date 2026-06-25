# Installing with pipx

[pipx](https://pipx.pypa.io/) is a tool for installing Python CLI applications in isolated environments. It does not require [uv](https://docs.astral.sh/uv/).

## Install Specify CLI

Pin a specific release tag for stability (check [Releases](https://github.com/github/spec-kit/releases) for the latest):

```bash
# Install a specific stable release (recommended — replace vX.Y.Z with the latest tag)
pipx install git+https://github.com/github/spec-kit.git@vX.Y.Z

# Or install latest from main (may include unreleased changes)
pipx install git+https://github.com/github/spec-kit.git
```

## Install a Local Nomos Checkout

If you cloned `nomos-sdd` locally and want to expose `specify` without activating that checkout's `.venv`, `pipx` can install the repo in editable mode:

```bash
pipx install -e /path/to/nomos-sdd
```

After that, from another repository:

```bash
specify nomos init
specify nomos demand create minha-demanda
```

For this Nomos fork, this is the documented alternative path. The primary recommendation remains `uv tool install --from /path/to/nomos-sdd specify-cli`.

## Verify

```bash
specify version
```

## Upgrade

```bash
pipx install --force git+https://github.com/github/spec-kit.git@vX.Y.Z
```

## Uninstall

```bash
pipx uninstall specify-cli
```

## Next steps

Head to the [Quick Start](../quickstart.md) to initialize your first project.
