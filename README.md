# Fourways Mall Guide

A responsive visitor guide published with GitHub Pages.

## Store directory updates

The source of truth is Fourways Mall's [public store directory](https://fourwaysmall.com/store-directory-all.php). `scripts/refresh-directory.py` reads the official listing and updates `mall-data.js`, preserving the names, published unit codes, telephone numbers and store links. If the source page changes unexpectedly or returns too few entries, the refresh stops without replacing the current snapshot.

The **Refresh directory and publish site** GitHub Actions workflow runs after a push, when manually requested, and every six hours. It commits a new directory snapshot only if the official listing changed, then deploys the refreshed site to GitHub Pages. GitHub schedule runs can be delayed, so updates are periodic rather than instantaneous.

To enable the publishing workflow, open the repository's **Settings → Pages** and select **GitHub Actions** as the source. The repository currently has a GitHub Pages site.

## Guided answers and AI setup

The guide can answer common directory questions and return matching official store listings without an API. Free-form AI responses use the secure Cloudflare Worker in `assistant-worker/`; the API key stays server-side and is never put in the website.

1. Create a Cloudflare account and install Wrangler (`npm install --global wrangler`).
2. From `assistant-worker/`, run `wrangler login` and then `wrangler secret put OPENAI_API_KEY`.
3. Deploy the Worker with `wrangler deploy`. The Worker includes a per-IP rate limit and accepts requests only from the configured site origin.
4. Set the deployed Worker URL as `assistantEndpoint` in `site-config.js`, then push that change to `main`.

AI requests use the OpenAI Responses API. OpenAI API usage may incur charges; set account spending limits before enabling the endpoint. Never commit the API key or a local `.dev.vars` file.

## GPS, indoor routes and entrance QR codes

The guide asks for location permission only when a visitor taps **Check my location**. Browser GPS can locate a phone outdoors, but it does not provide a reliable mall-level position or a walkable route indoors by itself.

The included printable QR poster at `qr-print.html` links to the website and can be placed at entrances. It is a general website QR; it does not identify which entrance a visitor scanned at. Entrance-aware QR codes and accurate indoor directions require current, approved floor maps, surveyed store and entrance coordinates, and a walkable route network from mall management. Those source materials were not present in this repository, so the guide does not fabricate entrances, map pins, or directions.

The available linked floor-plan PDF is dated 2024 and may not show current tenant locations. Use the mall's live directory for current store information.

## Run locally

Open `index.html` in a browser, or run a local static web server from the repository root. The site needs HTTPS for browser location and service-worker features; GitHub Pages provides HTTPS after it is enabled.
