---
name: docker-patterns
description: Design Dockerfiles with small images, deterministic builds, non-root users, and cache-friendly layers.
argument-hint: "[scope | file | goal]"
metadata:
  origin: VEX
  category: reference
  triggers: ["Dockerfile edits", "Container build failure", "Image hardening"]
---

# Docker Patterns

Best practices for writing efficient, secure, and maintainable Dockerfiles.

## When to Activate

- Creating or editing a `Dockerfile` or `docker-compose.yml`.
- Optimizing image size or build times.
- Securing container deployments.

## Core Principles

### 1. Multi-Stage Builds
Use multi-stage builds to keep final images small. Build dependencies in a fat image, copy only compiled artifacts to a slim runtime image.

```dockerfile
# Stage 1: Build
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# Stage 2: Runtime
FROM node:18-alpine
WORKDIR /app
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
CMD ["node", "dist/main.js"]
```

### 2. Cache Optimization (Order Matters)
Docker caches layers. Put instructions that change frequently (like `COPY . .`) as far down the Dockerfile as possible. Copy dependency files (`package.json`, `requirements.txt`) and install dependencies *before* copying the rest of the code.

```dockerfile
# ✅ Good: Cached correctly
COPY package.json package-lock.json ./
RUN npm ci
COPY . .

# ❌ Bad: Cache busted on every code change
COPY . .
RUN npm ci
```

### 3. Least Privilege (Non-Root User)
Never run your application as the root user inside the container.

```dockerfile
FROM alpine:3.18
RUN addgroup -S appgroup && adduser -S appuser -G appgroup
USER appuser
WORKDIR /home/appuser
# ... rest of setup
```

### 4. Specific Image Tags
Never use `:latest` in production. Pin to specific versions (e.g., `node:18.17.0-alpine`) to ensure reproducible builds.

### 5. `.dockerignore`
Always include a `.dockerignore` file to prevent copying `node_modules`, `.git`, `.env` files, and local build artifacts into the container. This reduces build context size and prevents secret leakage.

## Common Pitfalls

- **Leaking Secrets**: Using `ENV` or `ARG` for secrets. Use Docker BuildKit secrets (`--mount=type=secret`) or inject them at runtime via environment variables or secret managers.
- **Fat Images**: Using `ubuntu` or `debian` base images when `alpine` or `distroless` would suffice.
- **Zombie Processes**: Running a Node or Java app directly as PID 1 (`CMD ["node", "app.js"]`). PID 1 doesn't handle OS signals correctly. Use `dumb-init`, `tini`, or ensure the runtime handles signals properly.

## Verification

- `docker build -t myapp .` succeeds.
- `docker run myapp` starts successfully.
- `docker image ls` shows a reasonably small image size.
- `docker history myapp` shows expected layer caching.
