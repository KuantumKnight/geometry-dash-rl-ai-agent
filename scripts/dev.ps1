[CmdletBinding()]
param(
    [ValidateSet(
        "help",
        "setup",
        "format",
        "lint",
        "typecheck",
        "test",
        "test-offline",
        "test-live",
        "benchmark",
        "train",
        "evaluate"
    )]
    [string]$Task = "help",
    [switch]$ConfirmLive
)

$ErrorActionPreference = "Stop"

function Invoke-UvRun {
    param([Parameter(Mandatory)][string[]]$Arguments)

    & uv run @Arguments
    if ($LASTEXITCODE -ne 0) {
        exit $LASTEXITCODE
    }
}

function Require-LiveConfirmation {
    if (-not $ConfirmLive) {
        Write-Output "This task can focus Geometry Dash or send desktop input. Re-run with -ConfirmLive after verifying focus is safe."
        exit 2
    }
}

switch ($Task) {
    "help" {
        Write-Output "Usage: .\scripts\dev.ps1 -Task <name> [-ConfirmLive]"
        Write-Output "Tasks: setup, format, lint, typecheck, test, test-offline, test-live, benchmark, train, evaluate"
    }
    "setup" {
        & uv sync --dev
        if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    }
    "format" {
        Invoke-UvRun @("ruff", "format", "src", "tests", "tools")
    }
    "lint" {
        Invoke-UvRun @("ruff", "check", "src", "tests", "tools")
    }
    "typecheck" {
        Invoke-UvRun @("pyright")
    }
    "test" {
        Invoke-UvRun @("python", "-m", "unittest", "discover", "-s", "tests", "-v")
    }
    "test-offline" {
        Invoke-UvRun @("coverage", "run", "-m", "unittest", "discover", "-s", "tests", "-v")
        Invoke-UvRun @("coverage", "report")
    }
    "test-live" {
        Require-LiveConfirmation
        Invoke-UvRun @("python", "tools\\capture_action.py", "--help")
    }
    "benchmark" {
        Require-LiveConfirmation
        Invoke-UvRun @("python", "tools\\benchmark_env.py", "--help")
    }
    "train" {
        Write-Output "Training is not implemented. Complete the RL algorithm, reward, and checkpoint decisions first."
        exit 2
    }
    "evaluate" {
        Write-Output "Evaluation is not implemented. Complete the evaluation protocol and checkpoint format first."
        exit 2
    }
}
