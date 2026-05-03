# release-2.0 — Planning Notes

This file tracks the in-flight 2.0 release work for what was
`pretix-signature-question` and is becoming `pretix-signature-capture`.

The full backlog of issues is filed against the GitHub repo. This document
records the cross-cutting decisions that shape *how* we work, captures
context that doesn't belong in any single PR description, and serves as a
running log of progress.

## Working model

- Trunk for this release: the `release-2.0` branch.
- Every backlog issue gets its own feature branch off `release-2.0`.
- Each feature branch opens a PR back into `release-2.0` for individual
  review.
- When the entire 2.0 backlog has merged into `release-2.0`, we open one
  final PR from `release-2.0` into `main` for the actual release.

This means `main` stays at the 1.x line until the full 2.0 is ready to ship,
and reviewers can step through changes per-issue.

## Cross-cutting decisions

The following are conscious choices made up-front so individual PRs don't
have to relitigate them:

**Module rename, not just distribution rename.** Issue #1 renamed both the
PyPI distribution name (`pretix-signature-question` -> `pretix-signature-capture`)
*and* the Python module (`pretix_signature_question/` ->
`pretix_signature_capture/`). Doing both at once keeps the package
consistent (`pip install pretix-signature-capture` then
`import pretix_signature_capture`) and avoids dragging the old module name
through subsequent issues. Since 2.0 is already a breaking release, the
incremental cost of renaming the module is low.

**Authorship.** `pyproject.toml` lists Sarina Canelake
<scanelake@gmail.com> as author and maintainer. The CREDITS / acknowledgement
of the original `pretix-unofficial` fork lineage lives in the README.

**Repo URL.** The `homepage` URL in `pyproject.toml` and the URLs in the
README point to `github.com/sarina/pretix-signature-capture`, even though
the repo is currently named `pretix-signature-question`. The GitHub repo
will be renamed at release time (Issue #15) — doing it now would create a
window where the repo's name says "capture" but the default branch ships
"question," which is more confusing than the current 404.

**Compatibility window.** `compatibility = "pretix>=2026.0.0"` and
`requires-python = ">=3.11"`. We are explicitly not supporting older
Pretix; the modernization issues (#5-#7) rely on signals and conventions
that didn't exist in older releases.

**Versioning during development.** Pre-release versions (`2.0.0a1`,
`2.0.0a2`, ...) while we work the backlog. We cut `2.0.0` proper in the
release issue (#15).

**Translations are out of scope for 2.0.** The locale directory and
Makefile remain in the tree, but no compiled `.mo` files are produced or
shipped. Discovered during Issue #2 that the existing build hook hadn't
been firing under modern setuptools/PEP 517 anyway. A working translations
pipeline will be restored in a future release.

## Progress log

### Issue #1 — Rename package to pretix-signature-capture and refresh metadata

- Branch: `issue-1` -> merged into `release-2.0`
- Status: done

Changes that landed:

- Module directory renamed via `git mv`
  (`pretix_signature_question/` -> `pretix_signature_capture/`), plus the
  `static/` and `templates/` subdirectories.
- `pyproject.toml`: name, version-attr path, authors, maintainers, homepage,
  requires-python, entry-point key + value, keywords, description.
- `pretix_signature_capture/apps.py`: `PluginConfig.name`, `verbose_name`,
  `PretixPluginMeta.{name, author, description, compatibility}`,
  `RuntimeError` message version reference.
- `pretix_signature_capture/__init__.py`: `__version__` -> `2.0.0a1`.
- `pretix_signature_capture/signals.py`: `dispatch_uid` and template path.
- `pretix_signature_capture/templates/.../presale_head.html`: static URLs.
- `setup.cfg`: `known_first_party`, coverage `source`.
- `Makefile`: locale glob.
- `MANIFEST.in`: paths.
- `.update-locales.sh`: `DIR=` path (the `COMPONENTS=` Weblate ref is
  intentionally left alone — that script is broken in other ways post-fork;
  see follow-ups).
- `.github/workflows/{style,tests}.yml`: path globs (these workflows will
  be substantially rewritten in issue #3).
- `README.rst`: rewritten title/intro, install instructions, migration
  notes for users of the previous packages, acknowledgements, copyright.

Verification: built the wheel locally. Confirmed
`pretix_signature_capture-2.0.0a1-py3-none-any.whl` contains all expected
files at the new paths, and that the wheel metadata correctly reflects the
new identity. The `requires-python` constraint enforces correctly —
installs into Python 3.10 are rejected.

### Issue #2 — Remove deprecated distutils.commands entry point

- Branch: `issue-2` -> PR into `release-2.0`
- Status: ready for review

The original ticket said "remove the dead entry point because
`pretix-plugin-build` registers itself another way." Investigation found
that's not actually true — `pretix-plugin-build`'s wheel ships no
entry_points.txt. The entry point in our `pyproject.toml` was the *only*
way `CustomBuild` would have been wired in.

But it was still dead code, for a different reason: modern PEP 517 builds
using `setuptools.build_meta` (which we adopted in #1) don't honor the
`distutils.commands` entry-point group at all. I instrumented
`pretix_plugin_build.build` with marker prints and confirmed it was never
imported during a build, with or without our entry point present.

Concrete consequence: `compilemessages` was never running at build time, so
our wheels haven't been shipping `.mo` files. Confirmed by inspecting the
wheel artifact. This is a regression vs. the older
`pretix-signature-question-2` PyPI wheel, which does contain `.mo` files
(presumably built with an older toolchain that still honored the entry
point, or by a developer who ran `make` locally before publishing).

Per scoping decision: translation support is **out of scope for the 2.0
release**. The locale directory and Makefile remain in the tree for future
work, but no compiled translations are produced or shipped. README updated
to make this explicit and to drop the (currently no-op) `make` step from
the dev setup.

Changes landed:

- `pyproject.toml`: removed `[project.entry-points."distutils.commands"]`
  block; removed `pretix-plugin-build` from `[build-system].requires` (it
  was only there to make `CustomBuild` importable for the now-removed
  entry point).
- `README.rst`: removed step 5 ("Execute `make` ... to compile
  translations") from the dev setup; added a note explaining that
  translations are deferred to a future release.

Verification: rebuilt the wheel after the changes. Build deps shrink by
one package; resulting wheel is functionally identical to the Issue #1
baseline (same source files, same templates, same static assets, same
`[pretix.plugin]` entry point); the `[distutils.commands]` line is gone
from the wheel's `entry_points.txt`.

## Cross-cutting follow-ups discovered along the way

These came out of the per-issue work but don't naturally belong in any of
the existing tickets. Worth filing as new issues at some point.

- **Restore translations build.** The right path is probably to add an
  explicit setuptools `cmdclass` override (in `pyproject.toml` or a small
  `setup.py`) that runs `compilemessages` as part of `build_py`, replacing
  the dead-since-PEP-517 `distutils.commands` mechanism. Worth doing
  before the first non-English event tries to use the plugin in
  production.
- **License format deprecation.** Setuptools warned that
  `license = {file = "LICENSE"}` (TOML-table form) is deprecated in favor
  of `license = "Apache-2.0"` plus `license-files = ["LICENSE"]`. Builds
  break by 2027-Feb-18.
- **`.update-locales.sh` is broken post-fork.** The script targets the
  upstream Pretix Weblate component
  (`pretix/pretix-plugin-pretix-signature-question`), which we no longer
  have access to. Should be deleted or rewritten if/when we set up our own
  translation pipeline.
- **GitHub Actions workflows already exist** — Issue #3's premise that
  there are no workflows is wrong. Issue #3 should be re-scoped to:
  modernize the existing workflows (use modern action versions, fix the
  matrix, replace `setup.py sdist` with `python -m build`) and add the
  missing release-on-tag workflow.
