#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

if ! command -v uv >/dev/null 2>&1; then
  echo "Erro: 'uv' nao encontrado no PATH." >&2
  echo "Instale o uv e tente novamente: https://docs.astral.sh/uv/getting-started/installation/" >&2
  exit 1
fi

echo "Instalando Nomos localmente a partir de: ${REPO_ROOT}"
uv tool install --from "${REPO_ROOT}" specify-cli "$@"

echo
echo "Instalacao concluida. Teste em outro repositorio com:"
echo "  specify nomos init"
echo "  specify nomos demand create minha-demanda"
