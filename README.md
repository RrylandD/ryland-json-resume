# ryland-json-resume

JSON Resume source for [rylanddonovan.com](https://www.rylanddonovan.com). The PDF is built with [RenderCV](https://docs.rendercv.com) (`make pdf`) and published to the site repo; `output/` and `.generated/` stay gitignored.

## Local PDF

Requires Python 3.12+. RenderCV’s `full` extra bundles TinyTeX (no separate LaTeX install).

```sh
make pdf   # → output/resume.pdf
```

## Publish to the site

On push to `main` (resume content, design, scripts, or this workflow) or via **Actions → Publish CV → Run workflow**, GitHub Actions:

1. Runs `make pdf`
2. Copies `output/resume.pdf` and `resume.json` into [`personal-website-astro`](https://github.com/RrylandD/personal-website-astro) `public/`
3. Commits and pushes only if those files changed

Netlify then deploys `/resume.pdf` and `/resume.json`.

### Secret

Add **one** Actions secret on **this** repo (`ryland-json-resume` → Settings → Secrets and variables → Actions):

| Name | Purpose |
| --- | --- |
| `SITE_DEPLOY_TOKEN` | Fine-grained PAT that can push to `personal-website-astro` |

Create the token: GitHub → **Settings → Developer settings → Personal access tokens → Fine-grained tokens**.

- Resource owner: `RrylandD`
- Repository access: **Only select repositories** → `personal-website-astro`
- Permissions: **Contents: Read and write** (Metadata: Read is automatic)
- Expiration: set a reminder to rotate

Paste the token value as `SITE_DEPLOY_TOKEN`. Nothing is needed on Netlify or the site repo for the push itself; Netlify already deploys when `personal-website-astro` `main` updates.

**Deploy-key alternative:** generate an Ed25519 key, add the public key as a write-enabled deploy key on `personal-website-astro`, store the private key as `SITE_DEPLOY_KEY` here, and switch the site `actions/checkout` step to `ssh-key: ${{ secrets.SITE_DEPLOY_KEY }}` instead of `token`.

### Verify after merge

1. Add `SITE_DEPLOY_TOKEN` **before** merging this workflow (the first run on `main` will fail at the site checkout otherwise).
2. Merge the site PR (Download CV UI + `netlify.toml` headers), then this repo.
3. Confirm **Actions → Publish CV** succeeded (merge of this workflow file retriggers it).
4. On `personal-website-astro`, look for a commit `chore: publish CV from ryland-json-resume@…`.
5. After the Netlify deploy: [Download CV](https://www.rylanddonovan.com), [resume.pdf](https://www.rylanddonovan.com/resume.pdf), [resume.json](https://www.rylanddonovan.com/resume.json).
