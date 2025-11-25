QuantumNex Render Deployment

This file documents the production-grade Render setup for the repository.

Services created by render.yaml (branch: render/deploy-config):
- quantumnex-frontend (env: node): builds and serves the Next.js app in quantumnex-dashboard/
- quantumnex-api (env: docker): API server from repo root (app.js) using the root Dockerfile
- quantumnex-worker (env: docker): background worker that runs periodic optimization cycles

Managed resources created (placeholders in render.yaml):
- PostgreSQL: quantumnex-db  (DATABASE_URL will be provided by Render)
- Redis: quantumnex-redis  (REDIS_URL will be provided by Render)

Required repo checks before deploy:
- Ensure quantumnex-dashboard/package.json has build and start scripts (next build / next start)
- Ensure root app.js listens on process.env.PORT and binds to 0.0.0.0 (already implemented)
- Do NOT commit any secrets. Use Render dashboard to set secrets or use the managed DB/Redis

How Render references secrets and databases:
- DATABASE_URL is injected via "fromDatabase" in render.yaml
- REDIS_URL is injected via "fromService" mapping in render.yaml
- Add any RPC keys or private keys in the Render dashboard under Environment -> Secrets, then reference them via envVars

Quick deploy steps:
1. Push this branch (render/deploy-config) to GitHub
2. In Render dashboard, connect the repository (if not already connected)
3. Render will read render.yaml and create the configured services and managed DB/Redis
4. Provide any additional secrets (ALCHEMY/INFURA/RPC keys) in the Render dashboard
5. Monitor builds and logs; set health check path to /health for services if needed

Notes:
- The worker.js is a placeholder. Replace with real background tasks that connect to the DB/Redis and perform migrations/optimizations.
- If you prefer the frontend built and deployed as Docker instead of Node env, update render.yaml to use env: docker and dockerfilePath for the frontend.
