# Case Analyzer Frontend

## Requirements

- [ ] Basic interface which lets user upload court decision, chat with the system, and have a mult-turn conversation
- [ ] User authentication and log in feature
- [ ] Conversation histories for authenticated users

# Frontend Dev (migrated from Bun to Vite + npm)

## Getting Started

Install dependencies:

```bash
npm install
```

Run dev server (Vite):

```bash
npm run dev
```

Build for production:

```bash
npm run build
```

Preview the production build locally:

```bash
npm run preview
```

## Notes

- Bun-specific server (`src/index.tsx`) replaced by standard React entry `src/main.tsx`.
- `index.html` moved to project root per Vite convention.
- Removed `bun.lock`, `bunfig.toml`, and Bun scripts.
- Tailwind setup unchanged (processing now goes through Vite/PostCSS instead of Bun build).
- Ensure Node.js >= 18.

If you previously installed with Bun, remove old artifacts:

```bash
rm -rf node_modules bun.lock bun.lockb
npm install
```

Happy hacking!

## Landing Page Only Docker Image
A minimal container that serves just the public landing page (route `/`) and static assets without exposing authenticated app routes. Uses a Node 20 Alpine build stage and Nginx runtime.

Build the image:
```bash
docker build -f Dockerfile.landing -t clerk-landing:latest .
```

In repo root you can also run:
```bash
docker build -f frontend/Dockerfile.landing -t clerk-landing frontend
```

Run the container:
```bash
docker run --rm -p 8080:80 clerk-landing:latest
```

Visit:
```
http://localhost:8080/
```

Blocked routes (e.g. `/clerk`, `/api`) return 404.
