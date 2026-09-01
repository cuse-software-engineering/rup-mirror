# RUP 2002 Process Website — Archival Mirror

Frozen mirror of the **Rational Unified Process (RUP) 2002** hypertext, taken from the
unofficial academic mirror at <https://www.tesestec.com.br/pasteurjr/rup/> for use as a
stable citation target in software-engineering coursework
(see `cuse-software-engineering` assignment repos, e.g. `resources/rup-mirror` submodule).

- **Source:** https://www.tesestec.com.br/pasteurjr/rup/index.htm (static Apache mirror; files last modified 2013-04-04)
- **Fetched:** 2026-09-01
- **Contents:** 2,034 files, ~35 MB — process pages, workflow details, activities, artifacts, roles, guidelines, templates, examples, manuals, and the Real-Time add-in subset hosted by the source.

## Copyright

The Rational Unified Process is © IBM Corporation / Rational Software.
This snapshot is kept **unmodified, in a private repository, solely for educational
reference and link-rot protection** in university coursework. Do not make this
repository public and do not redistribute its contents. See `copyrite/copyrite.htm`
inside the mirror for the original notice.

## Browsing locally

Open [`index.htm`](index.htm) in a browser. Note that the original left-hand
navigation is a Java applet (`applet/ruptools/TreeBrowse.class`) that modern browsers
will not run. Use these plain-HTML entry points instead:

- [`sitemap/sitemap.htm`](sitemap/sitemap.htm) — full site map
- [`index/index.htm`](index/index.htm) — alphabetical index
- [`process/ovu_proc.htm`](process/ovu_proc.htm) — process overview
- [`process/glossary.htm`](process/glossary.htm) — glossary
- Requirements workflow details: `process/workflow/requirem/wfd_req.htm`

## How it was mirrored

Three `wget` passes (recursive, `--no-parent`, timestamping, no link rewriting — the
site uses relative links throughout, so it is browsable as-is):

1. Seeded from the 153 pages listed in the navigation applet's `applet/tree.dat`
   plus the sitemap/index/applet entry pages (the frameset alone links almost nothing).
2. Re-seeded from unresolved internal links found by a link-closure scan — this
   recovered subtrees only reachable through JavaScript-written links
   (`addin_realtime/`, `rpw_gen/`), which wget cannot parse.
3. Final pass for the six `process/plugins/ovu_*.htm` pages; converged with no new links.

Additional manual recovery:

- `applet/ruptools/**/*.class` (8 files) — applet classes found by transitively
  reading class references; not discoverable by wget.
- 13 images referenced with Windows backslash paths (e.g.
  `process/workflow/test/images\…gif`) — fetched at their forward-slash locations.

Remaining broken links (~468 unique targets) are **dead on the source mirror as
well** — chiefly the Wylie College course-registration example project
(`wyliecollegeexample/…`, linked from many artifact pages) and a handful of devkit
internals, none of which the source hosts. Every other internal link resolves inside
this repository (verified by the closure scan).
