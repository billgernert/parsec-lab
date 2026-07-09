# Sanitization checklist - what must NEVER be committed here

This is a **public** repository. Only the curated landing-page content belongs in it. The lab is
built in a private repository; nothing is mirrored here except the files on the allowlist below.
Before every commit, confirm none of the "never" categories have leaked in.

## Allowlist - the complete set of files that belong here

- `index.html` - the landing page (capabilities are described at a level that names no internal
  host, IP, or secret)
- `_headers` - Cloudflare Pages response headers
- `README.md`, `SANITIZATION.md`, `DEPLOY.md`, `LICENSE`

If a file is not one of these, it does not belong in this repo.

## Never commit here

- **Secrets of any kind** - tokens, API keys, passwords, PSKs, private keys, Vault paths or
  policies, credential IDs, connection strings, `.env` files.
- **Internal network detail** - internal hostnames and service subdomains, the internal AD domain
  name, IP addresses, subnet/VLAN layout, VM names or IDs, Cloudflare Tunnel connector IDs, and
  Access application names or policies. (The public site only ever names the apex `parsec-lab.com`.)
- **`CLAUDE.md` and internal ops docs** - `CLAUDE.md` is private-only by rule (it holds internal
  IPs/hostnames); likewise runbooks, architecture docs, the backlog, and the roadmap.
- **The job-search subsystem** - the jobsearch database, migrations, scored postings, prompts,
  mailbox data, and anything under `jobsearch/` or `postings/`.
- **The resume / CV** - the resume file and any resume text beyond the curated skills already on
  the page.
- **Pipeline and infrastructure source** - Jenkinsfiles, Ansible roles/playbooks, Terraform,
  inventory, `k8s/` manifests, `host_vars/`, `iam/`, `offboarded/`, `scripts/`.
- **Anyone else's identity** - departed users, service accounts, or any person other than the
  site owner.

## Before every commit

1. Skim the diff for anything that identifies internal infrastructure: IP addresses, host or VM
   names, internal subdomains, or the internal AD domain. The public page links only to
   `parsec-lab.com` and `github.com`.
2. No secrets - run gitleaks (or equivalent) if available.
3. If in doubt, it stays in the private repo.
