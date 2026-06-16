---
name: docker-compose
description: Setup docker-compose patterns for local dev and multi-service systems. Cover volumes, networking, environment variables, health checks, overrides, and dev vs. production build stages.
argument-hint: "[services | setup-target | environment]"
metadata:
  origin: VEX
---

# Docker Compose Patterns

Use this skill when orchestrating multiple containers for development, testing, or production parity.

## Triggers

- User asks to containerize local dev, run dependencies, add a database, cache, or broker.
- Repo has multiple apps, a backend + database, or a frontend + API.
- Setting up `docker-compose.yml`, `Dockerfile`, or `.env.example`.
- Fixing container networking, volume permissions, or hot-reload inside Docker.

## Inputs To Inspect

- `docker-compose.yml`, `docker-compose.override.yml`, `docker-compose.prod.yml`.
- `Dockerfile` for targets or stages (`dev`, `prod`, `builder`).
- `.env` template files.
- Run scripts or Makefile wrapping compose.
- Port numbers in config to map avoiding conflicts.
- Local volume mounting paths.

## Compose Setup Strategy

1. Separate data, application, and utility services.
2. Use named volumes for databases to persist between restarts.
3. Use bind mounts for application code to enable hot reload in dev.
4. Bind mount anonymous volumes over node_modules to hide host binaries.
5. Provide explicit `.env.example` mapping values for compose variables.
6. Configure health checks for strict dependency order (`condition: service_healthy`).
7. Expose ports on `localhost:` not `0.0.0.0` unless intended for network access.

## Standard Local Dev Stack

```yaml
version: '3.8' # Use for v2 compatibility

services:
  api:
    build:
      context: .
      target: dev
    ports:
      - "127.0.0.1:3000:3000"
    volumes:
      - .:/app
      - /app/node_modules
    environment:
      - DATABASE_URL=postgres://app_user:app_pass@db:5432/app_db
      - REDIS_URL=redis://cache:6379/0
      - NODE_ENV=development
    depends_on:
      db:
        condition: service_healthy
      cache:
        condition: service_started
    command: npm run dev

  db:
    image: postgres:16-alpine
    ports:
      - "127.0.0.1:5432:5432"
    environment:
      POSTGRES_USER: app_user
      POSTGRES_PASSWORD: app_pass
      POSTGRES_DB: app_db
    volumes:
      - pgdata:/var/lib/postgresql/data
      - ./scripts/init-db.sql:/docker-entrypoint-initdb.d/init.sql
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U app_user -d app_db"]
      interval: 5s
      timeout: 3s
      retries: 5

  cache:
    image: redis:7-alpine
    ports:
      - "127.0.0.1:6379:6379"
    volumes:
      - redisdata:/data

volumes:
  pgdata:
  redisdata:
```

## Profiles and Utilities

Group services so users can run subsets:

```yaml
  worker:
    build: .
    profiles: ["background", "all"]

  db-admin:
    image: dpage/pgadmin4
    profiles: ["tools", "all"]
```

## Dev vs Prod Dockerfile

```dockerfile
# Base dependencies
FROM node:22-alpine AS deps
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci

# Local dev stage with hot reload
FROM deps AS dev
COPY . .
CMD ["npm", "run", "dev"]

# Prod builder
FROM deps AS build
COPY . .
RUN npm run build && npm prune --production

# Prod runtime
FROM node:22-alpine AS prod
WORKDIR /app
RUN addgroup -S appgroup && adduser -S appuser -G appgroup
USER appuser
COPY --from=build --chown=appuser:appgroup /app/dist ./dist
COPY --from=build --chown=appuser:appgroup /app/node_modules ./node_modules
CMD ["node", "dist/index.js"]
```

## Verification Commands

```bash
docker compose config              # Validates YAML and merges overrides
docker compose up -d               # Starts services
docker compose ps                  # Shows running state and health
docker compose logs -f api         # Follow logs
docker compose down -v             # Clean up including data volumes
```

## Common Pitfalls

- Using `depends_on` without `condition: service_healthy` causes app to crash before DB starts.
- Missing `target: dev` in local compose points compose at prod stage without hot-reload.
- Hardcoding `localhost` inside a container to reach another container instead of service name.
- Bind mounting host `node_modules` into linux containers breaks native binaries.
- Running DB without named volume causes data loss on `docker compose down`.
- Ports exposed globally `3000:3000` instead of `127.0.0.1:3000:3000` bypass host firewall.

## Done Criteria

- Run `docker compose up` starts app without external dependencies.
- Code edits trigger hot-reload inside container.
- Container restarts do not lose database data.
- File ownership in host directory is not corrupted by root container writes.
