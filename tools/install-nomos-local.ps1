[CmdletBinding()]
param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$ToolArgs
)

$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = (Resolve-Path (Join-Path $scriptDir "..")).Path

if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
    Write-Error "uv nao encontrado no PATH. Instale o uv e tente novamente: https://docs.astral.sh/uv/getting-started/installation/"
}

Write-Host "Instalando Nomos localmente a partir de: $repoRoot"
uv tool install --from $repoRoot specify-cli @ToolArgs

Write-Host ""
Write-Host "Instalacao concluida. Teste em outro repositorio com:"
Write-Host "  specify nomos init"
Write-Host "  specify nomos demand create minha-demanda"
