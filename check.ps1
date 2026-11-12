param([string]$Phase = 'phase1')
$ErrorActionPreference = 'Stop'
$python = Join-Path $PSScriptRoot '.venv/Scripts/python.exe'
Set-Location -LiteralPath $PSScriptRoot
New-Item -ItemType Directory -Force -Path results | Out-Null
$log = Join-Path $PSScriptRoot "results/${Phase}_checks.txt"
function Run-Check([string[]]$Arguments) {
    "COMMAND: python $($Arguments -join ' ')" | Tee-Object -FilePath $log -Append
    & $python @Arguments 2>&1 | Tee-Object -FilePath $log -Append
    "EXIT: $LASTEXITCODE" | Tee-Object -FilePath $log -Append
    if ($LASTEXITCODE -ne 0) { throw "Check failed: $Arguments" }
}
Run-Check @('-m','nk_oil.cli','--help')
Run-Check @('-m','nk_oil.cli','inspect','--phase1')
Run-Check @('-m','nk_oil.cli','prepare','--phase1')
Run-Check @('-m','nk_oil.cli','init-db','--phase1')
Run-Check @('-m','pytest','-q')
Run-Check @('-m','ruff','check','.')
