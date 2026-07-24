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
.github/workflows/deploy.yml  CI: Zola build + deploy to GitHub Pages
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

## Deploy (GitHub Pages)

Hosted on GitHub Pages via GitHub Actions. Every push to `main` runs
[`.github/workflows/deploy.yml`](.github/workflows/deploy.yml), which builds the
site with Zola 0.22.1 and publishes it to the `github-pages` environment.
There is no `pages` branch to maintain.

The custom domain (`qdistro.org`) is set in the repository's **Settings -> Pages**.
DNS: point the apex `qdistro.org` at GitHub Pages (A/AAAA records) and set
`www.qdistro.org` as a CNAME to `qdistro.github.io`. Enable *Enforce HTTPS* once the
certificate is provisioned.

## License

GPL-3.0-or-later. See [LICENSE](LICENSE).
