param([string]$Phase = 'final')
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
Run-Check @('-m','nk_oil.cli','inspect','--mode','sample')
Run-Check @('-m','nk_oil.cli','prepare','--mode','sample')
Run-Check @('-m','nk_oil.cli','enhance','--mode','sample')
Run-Check @('-m','nk_oil.cli','queries','--mode','sample')
Run-Check @('-m','pytest','-q')
Run-Check @('-m','ruff','check','.')
