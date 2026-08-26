# Dependency security audit

The repository pins the audit tool in the `dev` dependency group so local and CI checks use the same executable. Run the audit from a locked environment:

```powershell
uv sync --locked --dev
uv export --locked --dev --no-emit-project --format requirements-txt --output-file audit-requirements.txt
uv run pip-audit --strict --disable-pip -r audit-requirements.txt
Remove-Item audit-requirements.txt
```

The export omits the repository's editable package because it is not published to PyPI; only locked third-party dependencies are audited. `--disable-pip` makes the audit use the OSV vulnerability database without an additional pip dependency-resolution pass.

GitHub Actions runs the same audit every Monday at 03:17 UTC and supports a manual `workflow_dispatch` run. The job installs only from `uv.lock`, uses read-only repository permissions, and fails when `pip-audit` reports a known vulnerability or an audit error.
