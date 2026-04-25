# khavan.net

Personal travel blog — static site deployed on Cloudflare Pages.

## Stack

- HTML / CSS / vanilla JS (single page, no framework)
- Cloudflare Pages (hosting, CDN, SSL)
- Cloudflare Web Analytics

## Deploy

```bash
npx wrangler pages deploy . --project-name=kha-travel
```

## Local dev

```bash
python3 serve.py
# http://localhost:3000
```

## Project structure

```
├── index.html      # Main page
├── 404.html        # Custom 404
├── favicon.svg     # KV monogram
├── robots.txt      # SEO
├── sitemap.xml     # SEO
├── _headers        # Security headers (Cloudflare Pages)
├── _redirects      # www → root redirect
└── tools/
    ├── serve.py          # Local dev server
    └── upload_photos.py  # Batch upload photos to R2
```

## Domains

- https://cloudsecop.net (primary)
- https://kha-travel.pages.dev (Cloudflare Pages)
