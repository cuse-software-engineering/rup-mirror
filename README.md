# RUP 2002 Process Website — Archival Mirror

Frozen mirror of the **Rational Unified Process (RUP) 2002** hypertext, taken from the
unofficial academic mirror at <https://www.tesestec.com.br/pasteurjr/rup/> for use as a
stable citation target in software-engineering coursework
(see `cuse-software-engineering` assignment repos, e.g. `resources/rup-mirror` submodule).

## Layout

| Path | What it is |
|---|---|
| [`original/`](original/) | The mirrored site, **byte-identical to the source — never edited**. Maps 1:1 to `https://www.tesestec.com.br/pasteurjr/rup/<path>`. |
| [`start.htm`](start.htm) | Added by us: modern front page — collapsible navigation tree (built from the applet's own data) + filter box + content pane. |
| [`_mirror_extras/`](_mirror_extras/) | Added by us: `build_start.py`, which generates `start.htm` from `original/applet/*.dat`; `fix_charset.py`, which audits the encoding of `original/` and writes the `charset=windows-1252` Content-Type rules into `vercel.json`. |
| [`vercel.json`](vercel.json) | Added by us: hosting config — `/` rewrites to `start.htm`, and the generated charset headers (see *Hosting*). |

- **Source:** https://www.tesestec.com.br/pasteurjr/rup/index.htm (static Apache mirror; files last modified 2013-04-04)
- **Fetched:** 2026-09-01
- **Contents:** 2,039 original files, ~35 MB — process pages, workflow details, activities, artifacts, roles, guidelines, templates, examples, manuals, and the Real-Time add-in subset hosted by the source.

## Copyright

The Rational Unified Process is © IBM Corporation / Rational Software.
This snapshot is kept **in a private repository, solely for educational reference and
link-rot protection** in university coursework. Everything under `original/` is
unmodified; the only additions are the files listed in the table above, which contain
no RUP content (the navigation tree is generated from the site's own data files at
view-build time). Do not make this repository public and do not redistribute its
contents. See `original/copyrite/copyrite.htm` for the original notice.

## Browsing locally

Open [`start.htm`](start.htm) — modern navigation, original pages rendered untouched
in the content pane. Deep-link a page as `start.htm#original/process/...`.

The original entry point [`original/index.htm`](original/index.htm) still works, but
its left-hand navigation is a Java applet (`original/applet/ruptools/TreeBrowse.class`)
that modern browsers will not run. Plain-HTML equivalents inside the original site:

- [`original/sitemap/sitemap.htm`](original/sitemap/sitemap.htm) — full site map
- [`original/index/index.htm`](original/index/index.htm) — alphabetical index
- [`original/process/ovu_proc.htm`](original/process/ovu_proc.htm) — process overview
- [`original/process/glossary.htm`](original/process/glossary.htm) — glossary
- Requirements workflow details: `original/process/workflow/requirem/wfd_req.htm`

## Hosting (Vercel)

Deployed at <https://rup-mirror.vercel.app/> (`/` rewrites to `start.htm`; original pages
live at `/original/<path>`). The original pages are Windows-1252 text (their `<meta>` says
iso-8859-1, but they use cp1252 smart quotes and dashes), while Vercel serves every text file
as `charset=utf-8` and the HTTP header beats the `<meta>` tag — so every no-break space and
smart quote rendered as `�`. `vercel.json` therefore pins
`Content-Type: …; charset=windows-1252` for `original/**/*.{htm,html,txt,dat}`. Those rules are
generated: after re-fetching the mirror, re-run `python3 _mirror_extras/fix_charset.py`
(`--dry-run` to only audit) instead of editing them by hand. Nothing under `original/` is
transcoded.

## How it was mirrored

Three `wget` passes (recursive, `--no-parent`, timestamping, no link rewriting — the
site uses relative links throughout, so it is browsable as-is):

1. Seeded from the 153 pages listed in the navigation applet's `applet/tree.dat`
   plus the sitemap/index/applet entry pages (the frameset alone links almost nothing).
2. Re-seeded from unresolved internal links found by a link-closure scan — this
   recovered subtrees only reachable through JavaScript-written links
   (`addin_realtime/`, `rpw_gen/`), which wget cannot parse.
3. Final pass for the six `process/plugins/ovu_*.htm` pages; converged with no new links.

Additional manual recovery (all from the same origin, all under `original/`):

- `applet/ruptools/**/*.class` (8 files) — applet classes found by transitively
  reading class references; not discoverable by wget.
- `applet/rpw_*_subtree.dat` (5 files) — tree data the applet lazy-loads for the
  Phases / Disciplines / Roles / Artifacts / Tools branches; nothing links them.
- 13 images referenced with Windows backslash paths (e.g.
  `process/workflow/test/images\…gif`) — fetched at their forward-slash locations.

Remaining broken links (~468 unique targets) are **dead on the source mirror as
well** — chiefly the Wylie College course-registration example project
(`wyliecollegeexample/…`, linked from many artifact pages) and a handful of devkit
internals, none of which the source hosts. Every other internal link resolves inside
this repository (verified by the closure scan).
