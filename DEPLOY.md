# Deploy - Cloudflare Pages

The site is static; Cloudflare Pages serves the repository root and redeploys on every push to the
default branch. No build step.

## One-time connection

1. Cloudflare dashboard -> **Workers & Pages** -> **Create** -> **Pages** -> **Connect to Git**.
2. Authorize and select the **`parsec-lab`** repository (production branch: `main`).
3. **Build settings:**
   - Framework preset: **None**
   - Build command: **(leave empty - there is no build)**
   - Build output directory: **`/`** (the files are at the repo root)
   - Root directory: **`/`**
4. **Save and Deploy.** Pages serves the files and gives a `*.pages.dev` URL to preview.
5. **Custom domain:** project -> **Custom domains** -> **Set up a custom domain** -> `parsec-lab.com`
   (and optionally `www`). The domain's DNS is already on Cloudflare, so Pages creates the record and
   provisions the certificate automatically.
6. The `_headers` file (CSP + security headers) is applied automatically - no dashboard config.

## Verify once: apex vs Access

The landing page is the **apex** `parsec-lab.com` and must **not** be behind a Cloudflare Access
policy (it is public). App subdomains keep their Tunnel + Access; confirm no Access application
matches the bare apex, and that the apex record points at the Pages project rather than a Tunnel
route.

## Updates

Every push to `main` auto-deploys. To change the page, edit `index.html` and push.
