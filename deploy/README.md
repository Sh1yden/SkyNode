# SkyNode Deployment

This repository deploys directly to the `skynode` namespace through GitLab CI.

## Required GitLab CI/CD Variables

Define these in the GitLab project or inherited group:

- `KUBE_CONFIG`
- `CI_DEPLOY_USER`
- `CI_DEPLOY_ACCESS_TOKEN`
- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_WEBHOOK_SECRET`
- `POSTGRES_PASSWORD`
- `VISUAL_CROSSING_KEY`
- `WEATHER_API_KEY`
- `OPEN_WEATHER_MAP_API_KEY`
- `GOOGLE_KEY`
- `MAIN_ADMIN_ID`

Recommended settings for secret variables:

- masked
- protected

## Runtime Values

The pipeline deploys with these fixed runtime settings:

- `PROJECT_STATUS=product`
- `BASE_WEBHOOK_URL=https://skynode.prod.birdegop.ru`
- `POSTGRES_HOST=postgres.data.svc.cluster.local`
- `POSTGRES_PORT=5432`
- `POSTGRES_DB=skynode`
- `POSTGRES_USER=skynode`
- `REDIS_HOST=valkey.skynode.svc.cluster.local`
- `REDIS_PORT=6379`

## Database

The PostgreSQL user and database must already exist:

- database: `skynode`
- user: `skynode`
- password: value of `POSTGRES_PASSWORD`

## Deploy Flow

1. Push to the default branch.
2. Run the `deploy production` job manually.
3. The job updates the runtime Secret and applies the Kubernetes manifests from `deploy/k8s/`.
