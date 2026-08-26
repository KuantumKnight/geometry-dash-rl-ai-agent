# Docstring policy

Public package APIs must have concise docstrings that explain their observable contract. Ruff enforces missing docstrings on public package methods that are easy to overlook (`D102` and `D107`) while preserving the project's existing imperative-style wording.

CLI entry points must have a module docstring describing the command's purpose and safety boundary. Their `main()` functions should have a docstring when they are reusable outside the module; parser helpers are implementation details and are not required to carry duplicate text already supplied to `argparse`.

When adding a public API or CLI, include its inputs, outputs, side effects, and live/offline requirement where those details are not obvious from the signature. Do not copy a library definition into a docstring; document this project's behavior.
