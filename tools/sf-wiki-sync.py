#!/usr/bin/env python3
"""Copies the book to the d77void wiki on SourceForge, one way.

    SF_WIKI_TOKEN=<bearer token> tools/sf-wiki-sync.py [--dry-run <dir>]

Every page in src/SUMMARY.md becomes the wiki page "Immutable - <title>",
and src/README.md with the table of contents becomes "Immutable Docs".
GitHub stays the only place where pages are written: each wiki page says so
at the top. Links between pages point to the wiki pages, and links to a
section get the "h-" the wiki puts in front of heading ids. A page dropped
from SUMMARY.md is not deleted from the wiki; remove it there by hand.

With --dry-run <dir>, writes the wiki pages as files in <dir> instead.
"""
import os
import re
import sys
import urllib.parse
import urllib.request

API = "https://sourceforge.net/rest/p/d77void/wiki/"
REPO = "https://github.com/d77void/immutable-docs"
SITE = "https://d77void.github.io/immutable-docs/"
INDEX = "Immutable Docs"
SRC = "src"


def summary():
    """[(section or None, title, path)] in SUMMARY.md order, intro excluded."""
    pages, section = [], None
    with open(os.path.join(SRC, "SUMMARY.md"), encoding="utf-8") as f:
        for line in f:
            if line.startswith("# ") and line.strip() != "# Summary":
                section = line[2:].strip()
            m = re.match(r"\s*- \[(.+?)\]\((.+?)\)", line)
            if m:
                pages.append((section, m.group(1), m.group(2)))
    return pages


def wiki_name(title):
    # A "/" would be read as a path in the wiki's address.
    return "Immutable - " + title.replace("/", "-")


def convert(text, path, names):
    """The page's Markdown as the wiki shows it: no first heading (the wiki
    shows the page name), links to other pages and to sections rewritten."""
    text = re.sub(r"\A# .*\n+", "", text)
    base = os.path.dirname(path)

    def link(m):
        label, target = m.group(1), m.group(2)
        if re.match(r"[a-z]+:", target):
            return m.group(0)
        file, _, anchor = target.partition("#")
        anchor = "#h-" + anchor if anchor else ""
        if not file:
            return "[%s](%s)" % (label, anchor)
        file = os.path.normpath(os.path.join(base, file))
        if file not in names:
            sys.exit("%s: link to %s, which is not in SUMMARY.md" % (path, file))
        return "[%s](%s%s)" % (label, names[file], anchor)

    return re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", link, text)


def header(path):
    return (
        "> This page is copied from [immutable-docs on GitHub](%s/blob/main/src/%s), "
        "where it is written and corrected; it is also on [the documentation site](%s). "
        "Changes made here are overwritten.\n\n" % (REPO, path, SITE)
    )


def post(name, text, token):
    data = urllib.parse.urlencode({"text": text}).encode()
    req = urllib.request.Request(
        API + urllib.parse.quote(name), data=data,
        headers={"Authorization": "Bearer " + token})
    with urllib.request.urlopen(req, timeout=60) as r:
        if r.status >= 300:
            sys.exit("%s: HTTP %d" % (name, r.status))


def main():
    dry = sys.argv[2] if sys.argv[1:2] == ["--dry-run"] else None
    token = os.environ.get("SF_WIKI_TOKEN", "")
    if not dry and not token:
        sys.exit("SF_WIKI_TOKEN is not set")

    pages = summary()
    names = {"README.md": INDEX}
    names.update({p: wiki_name(t) for _, t, p in pages})

    out = {}
    for _, title, path in pages:
        with open(os.path.join(SRC, path), encoding="utf-8") as f:
            out[names[path]] = header(path) + convert(f.read(), path, names)

    with open(os.path.join(SRC, "README.md"), encoding="utf-8") as f:
        intro = convert(f.read(), "README.md", names)
    toc, section = [], None
    for sec, title, path in pages:
        if sec != section:
            toc.append("\n### %s\n" % sec)
            section = sec
        toc.append("- [%s](%s)" % (title, names[path]))
    out[INDEX] = header("README.md") + intro + "\n## Contents\n" + "\n".join(toc) + "\n"

    for name, text in out.items():
        if dry:
            os.makedirs(dry, exist_ok=True)
            with open(os.path.join(dry, name + ".md"), "w", encoding="utf-8") as f:
                f.write(text)
        else:
            post(name, text, token)
        print(name)


if __name__ == "__main__":
    main()
