#!/usr/bin/env python3
"""Pin the character set Vercel serves for the mirrored pages (fixes the
"������" that shows up where Word put no-break spaces after heading numbers).

The pages under original/ are Word / FrontPage exports. Their bytes are
Windows-1252: the <meta> tags say iso-8859-1, but the files use 0x80-0x9F
smart quotes, dashes and bullets that only exist in cp1252 (browsers treat the
two names as the same encoding anyway). Vercel serves every text file with
"charset=utf-8", and the HTTP header beats the <meta> tag, so every non-ASCII
byte renders as U+FFFD.

original/ must stay byte-identical to the source, so this script does not
transcode anything. It audits the encoding of every text-like file, refuses to
continue if any file is not cp1252, and then writes Content-Type header rules
into vercel.json that declare charset=windows-1252 for the affected file
types. Re-run it if the mirror is ever re-fetched.

Usage:  python3 _mirror_extras/fix_charset.py [--dry-run]
"""
import argparse
import json
import os
import re
import sys
from collections import Counter, defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ORIGINAL = os.path.join(ROOT, "original")
VERCEL_JSON = os.path.join(ROOT, "vercel.json")
CHARSET = "windows-1252"

# Extension -> MIME type for every text-like file type in the mirror. Anything
# not listed (gif, jpg, pdf, class, zip, ...) is binary and never gets a charset.
MIME = {
    ".htm": "text/html",
    ".html": "text/html",
    ".txt": "text/plain",
    ".css": "text/css",
    ".xml": "text/xml",
    ".js": "text/javascript",
    ".dat": "text/plain",
}
META_CHARSET = re.compile(rb"charset=([-\w]+)", re.I)


def classify(data):
    """'ascii' | 'utf-8' | 'cp1252' | 'binary' for one file's bytes."""
    if not any(b >= 0x80 for b in data):
        return "ascii"
    try:
        data.decode("utf-8")
        return "utf-8"
    except UnicodeDecodeError:
        pass
    try:
        data.decode(CHARSET)
        return "cp1252"
    except UnicodeDecodeError:
        return "binary"


def audit():
    """Return ({ext: Counter(kind)}, Counter(declared charset), [(path, kind)])."""
    kinds = defaultdict(Counter)
    declared = Counter()
    problems = []
    for dirpath, _, files in os.walk(ORIGINAL):
        for name in files:
            ext = os.path.splitext(name)[1].lower()
            if ext not in MIME:
                continue
            path = os.path.join(dirpath, name)
            with open(path, "rb") as f:
                data = f.read()
            kind = classify(data)
            kinds[ext][kind] += 1
            if kind in ("utf-8", "binary"):
                problems.append((os.path.relpath(path, ROOT), kind))
            if MIME[ext] == "text/html":
                m = META_CHARSET.search(data)
                declared[m.group(1).decode().lower() if m else "(none)"] += 1
    return kinds, declared, problems


def header_rules(kinds):
    """One vercel.json header rule per MIME type that has cp1252 files."""
    exts_by_mime = defaultdict(list)
    for ext, counter in sorted(kinds.items()):
        if counter["cp1252"]:
            exts_by_mime[MIME[ext]].append(ext.lstrip("."))
    rules = []
    for mime, exts in sorted(exts_by_mime.items()):
        pattern = exts[0] if len(exts) == 1 else "(" + "|".join(exts) + ")"
        rules.append({
            "source": "/original/(.*)\\." + pattern,
            "headers": [{"key": "Content-Type", "value": f"{mime}; charset={CHARSET}"}],
        })
    return rules


def is_generated(rule):
    """True for the rules this script owns (Content-Type under /original/)."""
    return rule.get("source", "").startswith("/original/") and any(
        h.get("key", "").lower() == "content-type" for h in rule.get("headers", [])
    )


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--dry-run", action="store_true",
                    help="print the audit and the rules but do not write vercel.json")
    args = ap.parse_args()

    kinds, declared, problems = audit()
    print("Encoding audit of original/ (text-like files only):")
    for ext, counter in sorted(kinds.items()):
        detail = ", ".join(f"{k}={v}" for k, v in sorted(counter.items()))
        print(f"  {ext:6} {sum(counter.values()):5} files: {detail}")
    print("Declared <meta> charsets in HTML: "
          + ", ".join(f"{k}={v}" for k, v in declared.most_common()))
    if problems:
        print(f"\nERROR: {len(problems)} file(s) are not {CHARSET}; "
              "one charset header per file type would break them:", file=sys.stderr)
        for path, kind in problems[:20]:
            print(f"  {kind:7} {path}", file=sys.stderr)
        return 1

    rules = header_rules(kinds)
    with open(VERCEL_JSON, encoding="utf-8") as f:
        config = json.load(f)
    config["headers"] = [r for r in config.get("headers", []) if not is_generated(r)] + rules
    print("\nContent-Type rules for vercel.json:")
    for r in rules:
        print(f"  {r['source']:34} -> {r['headers'][0]['value']}")
    if args.dry_run:
        print("(dry run: vercel.json not written)")
        return 0
    with open(VERCEL_JSON, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)
        f.write("\n")
    print(f"Wrote {os.path.relpath(VERCEL_JSON, ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
