# qdistro.org site

Static site for qdistro.org, built with [Zola](https://www.getzola.org).

## Role in qdistro

This repo is the public website, not the product documentation source of truth.
Architecture, security model, developer setup, and component contracts live in
[../qdistro/doc](../qdistro/doc) and the sibling component READMEs. The site
should present the current project narrative and release notes without becoming
a second, divergent manual.

## Local

```sh
zola serve            # live-reload at http://127.0.0.1:1111
zola build            # writes ./public
zola check            # validates links, content, templates
```

## Layout

```
config.toml              site config + base_url
content/
  _index.md              homepage (template = index.html)
  blog/
    _index.md            blog index (template = section.html)
    *.md                 individual posts (template = page.html)
templates/
  base.html              shared shell (nav, footer)
  index.html             homepage
  section.html           blog index
  page.html              individual post
sass/style.scss          compiled to /style.css
.domains                 codeberg pages custom domain config
.woodpecker.yml          CI: build + push to `pages` branch
```

## Add a post

Create `content/blog/YYYY-MM-DD-slug.md` with frontmatter:

```toml
+++
title = "Post title"
date = 2026-05-14
description = "Short summary for meta tags."
[taxonomies]
tags = ["release"]
+++

Body in markdown.
```

## Deploy to Codeberg Pages

1. Push this repo to `codeberg.org/qdistro/qdistro-site`.
2. Generate an SSH deploy key: `ssh-keygen -t ed25519 -f deploy_key -N ""`.
3. Add `deploy_key.pub` as a deploy key with write access on the target repo
   (Settings → Deploy Keys, check "Enable Write Access").
4. Enable Woodpecker on the repo at <https://ci.codeberg.org>, add the
   private key as a secret named `deploy_key`.
5. Add Codeberg's pinned SSH host-key line as a secret named
   `codeberg_host_key` (for example, a `codeberg.org ssh-ed25519 ...` line
   verified out-of-band from Codeberg's published fingerprints).
6. Push to `main`. The pipeline builds with Zola and force-pushes
   `public/` to the `pages` branch.
7. DNS: CNAME `www.qdistro.org` → `qdistro.codeberg.page.`, and either
   ALIAS the apex or A-record it to Codeberg's Pages IPs (see Codeberg
   Pages docs for current addresses).

## License

GPL-3.0-or-later. See [LICENSE](LICENSE).
