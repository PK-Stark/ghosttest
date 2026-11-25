# THE GHOST — STARK TECH V2

A responsive, installable client-side PWA for iPhone, desktop and tablet. Official STARK palette: obsidian black, metallic gold, electric blue, gunmetal, with restrained tactical green status accents.

## Deploy to Cloudflare Pages

- Framework preset: **None**
- Build command: **(leave empty)**
- Build output directory: **/** (repository root)
- Root directory: **/**

Connect this repository to Cloudflare Pages. Every push to `main` will trigger a new deployment. No build step is required.

## Install

- iPhone: open the HTTPS deployment in Safari → Share → Add to Home Screen.
- Android: open the site in Chrome → Install app / Add to Home Screen.
- Desktop: use the browser install control when offered.

## Modules

- COMMAND: local clock, network state, best-effort battery support and quick links.
- PHANTOM: user-initiated geolocation and OpenStreetMap embed.
- SPECTRE: visual radar simulation and browser device-orientation compass where supported.
- BLACK VAULT: user-selected local files and localStorage field notes.
- OVERWATCH: Stark project and engineering-tool links.

## Platform limits

This is a web app, not an iOS system launcher. iOS does not allow web apps to replace SpringBoard, silently toggle Wi-Fi/Bluetooth, access arbitrary files, or control the flashlight. GPS and motion sensors require explicit permission and HTTPS. Radar contacts are simulated, not real sensor detections. Battery API support varies by browser and is generally unavailable on iOS Safari. External map tiles require internet.

## Privacy

No backend, analytics, account system, or coordinate upload is included. GPS is requested only after the user taps Acquire GPS. Notes are stored in local browser storage. Selected files are listed in the current browser session and are not uploaded.
