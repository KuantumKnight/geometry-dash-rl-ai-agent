# Branch Protection Guidance

The repository's default branch should require the complete offline quality
workflow before merging. Configure this in GitHub after confirming the exact
check names produced by the workflow.

Required status checks:

- Windows / Python 3.12
- Windows / Python 3.13

Recommended settings:

- Require a pull request before merging.
- Require the status checks above to pass.
- Require branches to be up to date before merging.
- Require at least one review for changes outside a solo experiment branch.
- Do not require live-game checks in default CI.
- Allow administrators to bypass only for documented emergency fixes.

The workflow currently verifies formatting, linting, typing, offline tests with
coverage, package build, and the absence of proprietary game files. Recheck
these names when the workflow changes.
