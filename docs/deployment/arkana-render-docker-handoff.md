# Astrologer-API Render Docker Handoff

This repo publishes Docker images to GHCR and dispatches immutable artifacts to `arkana-infra`.

## Workflows

- Staging workflow: `.github/workflows/release-staging.yml`
- Production workflow: `.github/workflows/release-production.yml`

Each workflow:
- Checks out with submodules (`submodules: recursive`).
- Builds and pushes Docker images to GHCR.
- Tags images as `<env>` and `<env>-<git_sha>`.
- Dispatches `repository_dispatch` to `arkana-infra` with the immutable digest artifact.

## Required GitHub config in this repo

- Secret: `INFRA_REPO_DISPATCH_TOKEN`
- Variable: `INFRA_REPO` (example: `seacortex/arkana-infra`)
- Optional variable: `INFRA_DISPATCH_EVENT_TYPE` (default used by workflows is `app_release`)

## Dispatch payload contract

The workflows dispatch this `client_payload`:

```json
{
  "service": "astrologer-api",
  "environment": "staging|production",
  "artifact": "ghcr.io/<owner_lc>/astrologer-api@sha256:<digest>",
  "source_repo": "<owner/repo>",
  "source_sha": "<commit-sha>"
}
```

## Container runtime contract

- Build image from `Dockerfile`.
- Runtime command inside container:

```bash
uv run uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

- Health endpoint:

```http
GET /health
```

Expected response:

```json
{"status":"OK"}
```
