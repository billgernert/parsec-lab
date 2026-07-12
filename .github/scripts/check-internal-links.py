#!/usr/bin/env python3
"""Internal-link checker for the public parsec-lab site (item 77 second-CI).

Read-only, offline, standard library only. Walks the given root, parses every .html, and for each
internal reference verifies the target resolves inside the repo:
  - relative href/src to a file (optionally with a #fragment): the file must exist, and if a
    fragment is given, an element with that id must exist in the target file;
  - a same-page #fragment: an element with that id must exist in this file.
External links (http, https, protocol-relative //, mailto:, tel:, data:) and empty/JS hrefs are
skipped - deployment and external availability are not this check's job (Cloudflare Pages owns
deploy; no network is touched). Exits non-zero and prints one line per broken link if any fail.

Usage: python3 check-internal-links.py [ROOT]   (ROOT defaults to the current directory)
"""
import os
import sys
import html.parser
import urllib.parse

REF_ATTRS = {"href", "src"}
EXTERNAL_PREFIXES = ("http://", "https://", "//", "mailto:", "tel:", "data:", "javascript:")


class Extractor(html.parser.HTMLParser):
    """Collect (attr-name, value) references and the set of element ids on the page."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.refs = []   # list of reference strings from href/src
        self.ids = set()  # element ids present in this file (for fragment resolution)

    def handle_starttag(self, tag, attrs):
        for name, value in attrs:
            if value is None:
                continue
            if name in REF_ATTRS:
                self.refs.append(value.strip())
            if name == "id":
                self.ids.add(value.strip())
            if name == "name" and tag == "a":  # legacy anchor targets
                self.ids.add(value.strip())


def parse_html(path):
    ex = Extractor()
    with open(path, encoding="utf-8", errors="replace") as fh:
        ex.feed(fh.read())
    return ex.refs, ex.ids


def main():
    root = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else ".")
    html_files = []
    for dirpath, _, files in os.walk(root):
        # skip VCS / CI internals
        if os.sep + ".git" in dirpath or os.sep + ".github" in dirpath:
            continue
        for fn in files:
            if fn.lower().endswith(".html"):
                html_files.append(os.path.join(dirpath, fn))

    # ids per file, parsed once
    page = {}   # abspath -> (refs, ids)
    for p in html_files:
        page[p] = parse_html(p)

    broken = []
    checked = 0
    for p in sorted(html_files):
        refs, ids = page[p]
        base = os.path.dirname(p)
        rel_self = os.path.relpath(p, root)
        for ref in refs:
            if ref.lower().startswith(EXTERNAL_PREFIXES) or not ref:
                continue
            if ref.startswith("#"):
                # same-page fragment
                frag = urllib.parse.unquote(ref[1:])
                checked += 1
                if frag and frag not in ids:
                    broken.append(f"{rel_self}: missing in-page anchor '#{frag}'")
                continue
            # relative or root-absolute path, possibly path#fragment or path?query
            parsed = urllib.parse.urlparse(ref)
            target_path = urllib.parse.unquote(parsed.path)
            if not target_path:
                continue
            # A leading "/" is site-root-absolute (resolve from the repo root, as the web server
            # does), otherwise resolve relative to this file's directory.
            if target_path.startswith("/"):
                abs_target = os.path.normpath(os.path.join(root, target_path.lstrip("/")))
            else:
                abs_target = os.path.normpath(os.path.join(base, target_path))
            # A directory link (trailing slash, or a real directory) serves its index.html.
            if target_path.endswith("/") or os.path.isdir(abs_target):
                abs_target = os.path.join(abs_target, "index.html")
            checked += 1
            if not os.path.exists(abs_target):
                broken.append(f"{rel_self}: broken link -> '{ref}' (no file {os.path.relpath(abs_target, root)})")
                continue
            if parsed.fragment and abs_target in page:
                frag = urllib.parse.unquote(parsed.fragment)
                if frag and frag not in page[abs_target][1]:
                    broken.append(f"{rel_self}: '{ref}' -> file OK but missing anchor '#{frag}'")

    print(f"internal-link check: {len(html_files)} HTML file(s), {checked} internal reference(s)")
    if broken:
        sys.stderr.write("BROKEN INTERNAL LINKS:\n")
        for b in broken:
            sys.stderr.write(f"  {b}\n")
        sys.stderr.write(f"{len(broken)} broken internal link(s).\n")
        sys.exit(1)
    print("all internal links resolve")


if __name__ == "__main__":
    main()
