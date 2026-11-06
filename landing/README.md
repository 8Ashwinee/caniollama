# caniollama landing page

Static page: `index.html` + `config.js`. No build step.

## Deploy

Set the publish/output directory to `landing` and leave the build command empty.

- **Vercel:** New Project → import repo → Root Directory `landing`, Framework "Other", no build command.
- **Netlify:** Base directory `landing`, publish directory `landing` (or `.` relative to base), build command empty.
- **Cloudflare Pages:** Build command empty, build output directory `landing`.

Then add a custom domain (e.g. `caniollama.ghimireanjal.com.np`) as a CNAME to the host's target.

## Live registry lookup

The "Query the registry" panel only calls the backend when the page is served from `localhost`/`127.0.0.1`
(run `uv run uvicorn compat_registry.main:app` in `compat-registry/` and open `landing/index.html` via a local server,
e.g. `python3 -m http.server -d landing 5500`). On the public deploy it shows self-host steps instead.
Change the backend URL in `config.js`.

## Preview locally

```bash
python3 -m http.server -d landing 5500   # http://localhost:5500
```
