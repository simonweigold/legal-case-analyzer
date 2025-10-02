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
