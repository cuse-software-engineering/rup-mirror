#!/usr/bin/env python3
"""Generate start.htm - a modern navigation front page for the RUP 2002 mirror.

Reads the Java tree applet's own data files (applet/tree.dat plus the five
rpw_*_subtree.dat files it lazy-loads) and emits one self-contained HTML page:
collapsible tree sidebar + type-to-filter box + content iframe. No original
site file is modified; the content pages load untouched in the iframe.

Usage:  python3 _mirror_extras/build_start.py
"""
import html
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APPLET = os.path.join(ROOT, "original", "applet")
OUT = os.path.join(ROOT, "start.htm")


def parse_dat(path, base_depth=0):
    """Return [(depth, title, root_relative_url_or_None)] for one .dat file,
    splicing in *_subtree.dat files the way the applet lazy-loads them."""
    nodes = []
    with open(path, encoding="latin-1") as f:
        for line in f:
            s = line.strip()
            if not s or "*" not in s:
                continue
            parts = s.split("*")
            if len(parts) < 3 or not parts[0].isdigit():
                continue  # header line naming the icon zip
            depth = int(parts[0]) + base_depth
            title, url = parts[1].strip(), parts[2].strip()
            if url.endswith("_subtree.dat"):
                nodes.append((depth, title, None))
                nodes.extend(parse_dat(os.path.join(APPLET, url), depth + 1))
            else:
                url = re.sub(r"^\.\./", "", url)
                nodes.append((depth, title, "original/" + url if url else None))
    return nodes


def build(nodes):
    root = {"children": []}
    stack = [(-1, root)]
    for depth, title, url in nodes:
        node = {"title": title, "url": url, "children": []}
        while stack[-1][0] >= depth:
            stack.pop()
        stack[-1][1]["children"].append(node)
        stack.append((depth, node))
    return root["children"]


def render(nodes):
    out = []
    for n in nodes:
        t = html.escape(n["title"])
        if n["url"]:
            label = '<a href="%s" target="content">%s</a>' % (html.escape(n["url"]), t)
        else:
            label = '<span class="fold">%s</span>' % t
        if n["children"]:
            out.append(
                "<details><summary>%s</summary><div class=kids>%s</div></details>"
                % (label, render(n["children"]))
            )
        else:
            out.append("<div class=leaf>%s</div>" % label)
    return "".join(out)


PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>RUP 2002 &mdash; Mirror</title>
<style>
:root {
  --bg: #ffffff; --panel: #f6f7f9; --border: #d9dde3; --text: #1c2733;
  --muted: #5b6b7b; --accent: #0b57d0; --hover: #e9eef5;
}
@media (prefers-color-scheme: dark) {
  :root {
    --bg: #14181d; --panel: #1b2129; --border: #303844; --text: #dde4ec;
    --muted: #8b99a9; --accent: #7ab0ff; --hover: #232c37;
  }
}
* { box-sizing: border-box; }
html, body { height: 100%; margin: 0; }
body {
  font: 14px/1.45 system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
  color: var(--text); background: var(--bg);
  display: grid; grid-template-rows: auto 1fr; grid-template-columns: 340px 1fr;
  grid-template-areas: "header header" "nav content";
}
header {
  grid-area: header; display: flex; align-items: baseline; gap: 1.25em;
  padding: .6em 1em; background: var(--panel); border-bottom: 1px solid var(--border);
  flex-wrap: wrap;
}
header h1 { font-size: 1.05em; margin: 0; font-weight: 600; }
header h1 small { color: var(--muted); font-weight: 400; }
header a { color: var(--accent); text-decoration: none; font-size: .92em; }
header a:hover { text-decoration: underline; }
nav {
  grid-area: nav; overflow-y: auto; background: var(--panel);
  border-right: 1px solid var(--border); padding: .5em .4em 2em;
}
#filter {
  width: 100%; padding: .45em .6em; margin: 0 0 .5em;
  border: 1px solid var(--border); border-radius: 6px;
  background: var(--bg); color: var(--text); font: inherit;
}
#filter:focus { outline: 2px solid var(--accent); outline-offset: -1px; }
#tree { font-size: .95em; }
#tree details { margin: 0; }
#tree .kids { margin-left: .95em; border-left: 1px solid var(--border); padding-left: .35em; }
#tree summary { cursor: pointer; padding: .12em .3em; border-radius: 4px; list-style-position: outside; }
#tree summary:hover, #tree .leaf:hover { background: var(--hover); }
#tree .leaf { padding: .12em .3em .12em 1.15em; border-radius: 4px; }
#tree a { color: var(--text); text-decoration: none; }
#tree a:hover { color: var(--accent); }
#tree .fold { color: var(--muted); font-weight: 600; font-size: .92em; }
#tree .hide { display: none; }
iframe { grid-area: content; width: 100%; height: 100%; border: 0; background: #fff; }
@media (max-width: 720px) {
  body { grid-template-columns: 1fr; grid-template-rows: auto auto 1fr;
         grid-template-areas: "header" "nav" "content"; }
  nav { max-height: 40vh; border-right: 0; border-bottom: 1px solid var(--border); }
}
</style>
</head>
<body>
<header>
  <h1>Rational Unified Process <small>2002 mirror</small></h1>
  <a href="original/process/ovu_proc.htm" target="content">Overview</a>
  <a href="original/sitemap/sitemap.htm" target="content">Site&nbsp;Map</a>
  <a href="original/index/index.htm" target="content">A&ndash;Z&nbsp;Index</a>
  <a href="original/process/glossary.htm" target="content">Glossary</a>
  <a href="original/index.htm" target="_blank" rel="noopener" title="Original frameset (applet navigation does not run in modern browsers)">Original&nbsp;home</a>
</header>
<nav>
  <input id="filter" type="search" placeholder="Filter pages&hellip; (__COUNT__ entries)" aria-label="Filter navigation tree">
  <div id="tree">__TREE__</div>
</nav>
<iframe id="content" name="content" src="original/process/ovu_proc.htm" title="Page content"></iframe>
<script>
(function () {
  var tree = document.getElementById('tree');
  var box = document.getElementById('filter');
  var frame = document.getElementById('content');

  // A link inside <summary> should navigate the iframe, not toggle the folder.
  tree.addEventListener('click', function (e) {
    var a = e.target.closest('a');
    if (a) {
      if (a.closest('summary')) e.preventDefault(), frame.src = a.getAttribute('href');
      try { history.replaceState(null, '', '#' + a.getAttribute('href')); } catch (err) {}
    }
  });
  document.querySelector('header').addEventListener('click', function (e) {
    var a = e.target.closest('a[target=content]');
    if (a) { try { history.replaceState(null, '', '#' + a.getAttribute('href')); } catch (err) {} }
  });
  if (location.hash.length > 1) frame.src = decodeURIComponent(location.hash.slice(1));

  var timer;
  box.addEventListener('input', function () { clearTimeout(timer); timer = setTimeout(apply, 120); });
  function apply() {
    var q = box.value.trim().toLowerCase();
    var groups = tree.querySelectorAll('details, .leaf');
    if (!q) {
      groups.forEach(function (el) { el.classList.remove('hide'); if (el.tagName === 'DETAILS') el.open = false; });
      return;
    }
    groups.forEach(function (el) { el.classList.add('hide'); });
    tree.querySelectorAll('a, .fold').forEach(function (el) {
      if (el.textContent.toLowerCase().indexOf(q) === -1) return;
      var p = el.closest('.leaf, details');
      while (p && p !== tree) {
        p.classList.remove('hide');
        if (p.tagName === 'DETAILS') p.open = true;
        p = p.parentElement.closest('details');
      }
      var d = el.closest('summary') && el.closest('details');
      if (d) d.querySelectorAll('.hide').forEach(function (x) { x.classList.remove('hide'); });
    });
  }
})();
</script>
</body>
</html>
"""


def main():
    nodes = parse_dat(os.path.join(APPLET, "tree.dat"))
    tree = build(nodes)
    n_links = sum(1 for _, _, u in nodes if u)
    page = PAGE.replace("__TREE__", render(tree)).replace("__COUNT__", str(n_links))
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(page)
    print("wrote %s: %d nodes (%d linked), %.0f KB"
          % (os.path.relpath(OUT, ROOT), len(nodes), n_links, len(page) / 1024))


if __name__ == "__main__":
    main()
