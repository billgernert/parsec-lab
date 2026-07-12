# Skills portfolio (`site/skills/`)

A static, multi-page skills portfolio for parsec-lab.com. The index groups every
capability I operate in AutomationLab into six categories; each capability links to its
own writeup page. Plain HTML + one shared stylesheet - no framework, no build step, no
JavaScript. It deploys as-is with the rest of `site/` on Cloudflare Pages.

This is **additive**: it does not touch `site/index.html`. The parent site links here when
ready; until then these pages stand on their own under `/skills/`.

## Files

```
site/skills/
  style.css                 shared stylesheet (palette + type inherited from site/index.html)
  index.html                category grid; every skill is a clickable card
  <skill>.html              one page per skill, all from the same template
  PUBLISHING-CHECKLIST.md   HARD scrub gate - read before publishing anything
  README.md                 this file
```

## Adding a skill = copy one file

There is no generator to run and no config to edit by hand beyond one card. Two steps:

1. **Copy a page.** Duplicate an existing skill page as `<new-skill>.html`. All 27 pages are
   now written up, so copy any filled example (`proxmox.html`, `grafana.html`,
   `incident-postmortem.html` are good structural references) and clear the sections you have
   not written yet back to the `Writeup coming` placeholder. Then edit, in the copied file only:
   - the `<title>` and `<meta name="description">`
   - the breadcrumb's `<span class="here">` label
   - the `<span class="badge" data-accent="...">` category label and accent
     (`cyan` or `green` - see the table below)
   - the `<h1>` name and the `<p class="descriptor">` one-liner
   - each `<section class="block">` - replace the `Writeup coming` placeholder with content

2. **Add one card to `index.html`.** In the matching `<section class="category">`, copy an
   existing `<a class="skill-card">` block, point its `href` at your new file, and set the
   name + description. Use `data-status="live"` once the page has real content (it lights the
   status dot green); leave `data-status="coming"` while it is still a placeholder.

That is the whole workflow. No other file changes.

## The page template

Every skill page has the same seven sections, in order:

1. **What it is & why I use it**
2. **How I use it in the lab**
3. **Architecture** - diagram placeholder (`<div class="frame">`) until a scrubbed diagram exists
4. **In action** - screenshot placeholder (`<div class="frame">`) until a scrubbed screenshot exists
5. **Lessons learned & gotchas**
6. **Impact**
7. **Code & further reading** - scrubbed repo link (disabled placeholder until a public-safe repo exists)

Unwritten prose sections show a tasteful `<div class="coming">Writeup coming</div>` placeholder,
so a half-finished page still looks intentional rather than broken.

## Category accents

The index alternates accent color per category for visual rhythm; keep a page's badge accent
matching its category:

| Category                    | `data-accent` |
|-----------------------------|---------------|
| Platform & Orchestration    | `cyan`        |
| CI/CD & GitOps              | `green`       |
| Security & Identity         | `cyan`        |
| Observability               | `green`       |
| Networking & Edge           | `cyan`        |
| Automation & Tooling        | `green`       |

## Design

Palette and type are inherited verbatim from `site/index.html` so the skills area reads as one
continuation of the site, not a bolt-on: dark navy `#0a0e1a` ground, cyan `#00d4ff` primary,
green `#00ff96` accent, slate `#4a6080` muted, pale `#e0e8ff` text; Share Tech Mono for labels
and data, Exo 2 for prose. Single committed dark theme, matching the parent site.

## Before you publish

**Read `PUBLISHING-CHECKLIST.md` and clear every gate.** This site is public. No internal IPs,
no internal hostnames, no secrets or fingerprints in screenshots, nothing that maps the attack
surface. The checklist includes a one-line `git grep` gate that must print nothing before commit.
