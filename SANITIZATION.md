# Sanitization - what may be published here, and what must NEVER be

This is a **public** repository. This file is the **authority** for what is allowed to exist in it.
If a file is not covered below, it does not belong here.

The lab is built in a private repository. Nothing reaches this one except what is listed here, and
most of it arrives through a fail-closed scrub gate rather than by hand.

## Two classes of content, and only one of them has a machine gate

Knowing which class a file is in tells you what is actually protecting it.

### A. Sync-managed (a gate scans this before every push)

The `sync-public-site` pipeline in the private repo owns these paths. It stages the exact publish set,
runs a **fail-closed scrub gate** over it (any internal IP, internal hostname, internal domain, Vault
port, private key, or fingerprint fails the build and nothing is cloned or pushed), and only then
mirrors. `skills/`, `roadmap/`, `ai/`, `projects/`, and `platform/` are mirrored **with deletion**: a
page deleted in the private repo is deleted here.

| Path | What it is |
|------|------------|
| `index.html` | the landing page |
| `_headers` | response headers (CSP + security headers) |
| `skills/` | the capability pages + the shared `style.css` |
| `roadmap/` | the public roadmap (its facts block is generated) |
| `ai/` | how AI is used |
| `projects/` | the pipeline stories |
| `platform/` | the subsystem writeups |
| `diagram/` | the lab architecture (a public rendition; the internal diagram is never published) |
| `writeups/` | long-form writeups (adopted into the gate 2026-07-15; was hand-committed) |
| `SANITIZATION.md` | this file, published by the gate it describes |

**Do not hand-edit these here.** The next sync overwrites them, and your edit skips the scrub gate on
the way in. Change them in the private repo's `site/` and let the pipeline publish.

### B. Hand-committed (a human is the ONLY gate)

The pipeline never touches these. Nothing scans them. They are here because a person put them here,
and a person is the entire reason they are safe.

| Path | What it is |
|------|------------|
| `README.md`, `LICENSE`, `DEPLOY.md` | repo furniture |
| `.github/` | the site-ci workflow + its link checker (deliberately outside the sync allowlist, so the scrub gate's surface stays minimal) |

Everything in class B must be checked against "Never publish here" below **by reading it**, before it
is committed. There is no second net.

## Images

Images are allowed **only** inside a sync-managed page directory (`skills/`, `ai/`, `projects/`,
`platform/`, `roadmap/`), so that they travel with the pages that reference them and are mirrored with
deletion like everything else.

**But understand what the gate does and does not do for them.** The scrub gate greps the publish set
as **text**. It cannot read pixels. A screenshot showing an internal hostname, an IP address, a VM
name, a VLAN, or a Vault path **passes the gate and publishes**, because to the gate it is a blob of
bytes with no matches in it.

So for an image the gate is a human, and this is that human's checklist. Before committing any image:

- **No browser window.** No URL bar, no tabs, no bookmarks bar. Capture the page region only: the URL
  is an internal hostname and the bookmark bar is a map of the estate.
- **No internal hostnames or VM names** anywhere in the frame: titles, legends, axis labels, tables,
  tooltips, variable dropdowns. This is what usually kills an infrastructure screenshot.
- **No IP addresses, subnets, or VLAN ids.**
- **No internal domain, Vault paths or policy names, datasource URLs, Access application names, or
  tunnel connector ids.**
- **Nobody else's identity**: no user or service-account names other than the site owner.
- **Crop, do not redact.** A black box over text advertises that something was there, and a portfolio
  page should not look censored. If it cannot be framed clean, it does not ship.
- **Date it.** A screenshot is a dated snapshot, not a live fact: it cannot be regenerated the way the
  roadmap's facts block is. Caption it with its capture date, and never repeat a number from an image
  as a claim in prose.

If an image cannot satisfy every line above, leave it out. The page is better one image short than one
internal string long, and a public leak is irreversible.

## Never publish here

- **Secrets of any kind** - tokens, API keys, passwords, PSKs, private keys, Vault paths or policies,
  credential ids, connection strings, `.env` files.
- **Internal network detail** - internal hostnames and service subdomains, the internal AD domain
  name, IP addresses, subnet/VLAN layout, VM names or ids, tunnel connector ids, and Access
  application names or policies. The public site only ever names the apex `parsec-lab.com`.
- **Anything only a picture would leak** - see Images above. The scrub gate will not catch it.
- **`CLAUDE.md` and internal ops docs** - private-only by rule (they hold internal IPs/hostnames);
  likewise runbooks, architecture docs, the backlog, and the roadmap source.
- **The job-search subsystem** - the database, migrations, scored postings, prompts, mailbox data, and
  anything under `jobsearch/` or `postings/`. Employer names and posting content are a live target
  list; they never appear here, including inside an image or a writeup.
- **The resume / CV** - the resume file and any resume text beyond the curated skills already on the
  page.
- **Pipeline and infrastructure source** - Jenkinsfiles, Ansible roles/playbooks, Terraform,
  inventory, `k8s/` manifests, `host_vars/`, `iam/`, `offboarded/`, `scripts/`.
  **Short code excerpts are allowed** on a sync-managed page when they carry no internal string: they
  go through the scrub gate like any other page text. Publishing a whole file does not.
- **Internal issue or PR numbers** - they are references to a private tracker that a reader here
  cannot follow.
- **Anyone else's identity** - departed users, service accounts, or any person other than the site
  owner.

## Before every commit to this repo

1. **Which class is it?** If it is class A (sync-managed), you should not be hand-editing it at all -
   change it in the private repo instead.
2. **If it is class B, read it.** Every line, against "Never publish here". You are the only gate.
3. **If it is an image, work the image checklist** above. The scrub gate is blind to it.
4. Skim the diff for anything that identifies internal infrastructure: IPs, host or VM names, internal
   subdomains, the internal AD domain.
5. No secrets - run gitleaks (or equivalent) if available.
6. **If in doubt, it stays in the private repo.** A leak here cannot be undone: assume it is mirrored,
   cached, and indexed the moment it lands.

## Closed: `writeups/`, and the image that proved the rule

`writeups/` used to be class B, outside the mapping, unscanned. It was **adopted into the gate on
2026-07-15** and is class A now. Its history is worth keeping, because it is the reason the image
rules above exist in this shape.

It held a long-form writeup and a **stage-by-stage diagram image**, both hand-published. The writeup
was clean. The image was not: an internal **Vault path** and the **internal AD domain** were legible
in it, and it had been public since the day it went up. It reached the public repo through exactly
the two-part hole described above, both halves at once: it was **pixels**, so the grep went straight
past it, and it was **outside the mapping**, so the gate never walked it in the first place.

- **The image was removed** by the gate, not by hand: adopting `writeups/` brought it under
  mirror-with-delete, and the first publish afterwards deleted the image because it is not in
  `site/writeups/`. If a replacement is ever wanted, it must pass the image checklist above first.
- **Nothing was rotated, deliberately.** A Vault *path* is not a secret value and the AD domain is a
  name: the exposure was internal **naming**, not credentials. Read that as calibration, not comfort.
- **The public git history still has it, and that is an accepted decision** (operator ruling,
  2026-07-15). Removing a file from `main` does not purge it from history: anyone can fetch it from
  an older commit. A history rewrite of a **public** repo was judged not worth its cost for a naming
  disclosure - it means force-pushing a repo other people may have cloned, and caches and forks keep
  their copy regardless, so the purge would be partial theatre. The posture is **takedown-forward**:
  stop the exposure now, do not pretend it never happened. If something on the never-list ever leaks
  that *is* a credential, that calculus changes completely and the answer is rotate first, then worry
  about history.

The lesson this file exists to carry: **the gate protects what it can read, in the paths it walks.**
Anything outside either bound is protected by a person, and a person needs a checklist.
