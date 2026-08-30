# Security Policy

## Scope

The tools in this repository can focus a local Geometry Dash window and send
keyboard or mouse input. Treat them as desktop-control software and run them
only when the target window and surrounding desktop are safe.

## Reporting

Report security issues privately through GitHub's private vulnerability
reporting flow when it is enabled for the repository. Do not publish secrets,
personal desktop captures, usernames, local paths, game binaries, extracted
game assets, or proprietary recordings in an issue or pull request.

Include a minimal reproduction, affected commit, expected behavior, actual
behavior, and sanitized logs. The default CI suite must remain offline and
must never download or launch Geometry Dash.

## Live-control safety

Use the documented Ctrl+Shift+F12 emergency-stop host binding. Stop a session
immediately if focus or state detection is wrong. The project is not affiliated
with RobTop Games, and users must supply their own legitimate game copy.
