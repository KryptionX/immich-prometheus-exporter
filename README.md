# Immich Prometheus Exporter

Prometheus exporter for Immich. Exposes metrics for photos, videos, storage usage, users, and albums.

## Features

- Photo/video counts (per user and total)
- Storage usage per user
- Album counts (owned/shared)
- Server info and availability
- Ready for multi-arch (amd64, arm64)

## Quick Start (Pull from GHCR)

```bash
# Set your Immich URL and API key
export IMMICH_URL=http://immich:2283
export IMMICH_API_KEY=your-key

docker run -d \
  -e IMMICH_URL=$IMMICH_URL \
  -e IMMICH_API_KEY=$IMMICH_API_KEY \
  -e EXPORTER_PORT=9700 \
  -e SCRAPE_INTERVAL=60 \
  -p 9700:9700 \
  ghcr.io/kryptionx/immich-prometheus-exporter:latest
```

## Configuration

- `IMMICH_URL` (default: `http://localhost:2283`)
- `IMMICH_API_KEY` (required) — create in Immich UI with permissions: `serverInfo.read`, `user.read`, `album.read`
- `EXPORTER_PORT` (default: `9700`)
- `SCRAPE_INTERVAL` seconds (default: `60`)

## Metrics (sample)

- `immich_user_images_count{user_id, user_name}`
- `immich_user_videos_count{user_id, user_name}`
- `immich_user_quota_usage_bytes{user_id, user_name}`
- `immich_album_count{user_id, user_name, album_type}`
- `immich_server_photos_total`
- `immich_server_videos_total`
- `immich_up`

## Local Development

```bash
git clone https://github.com/KryptionX/immich-prometheus-exporter
cd immich-prometheus-exporter

# Build
docker build -t immich-exporter:dev .

# Run locally
docker compose up
```

## Portainer Deployment

Use `portainer-stack.yml` in the Portainer stack editor. Set env vars `IMMICH_URL` and `IMMICH_API_KEY` in the UI. Image: `ghcr.io/kryptionx/immich-prometheus-exporter:latest`.

## Prometheus Scrape Config

```yaml
scrape_configs:
  - job_name: "immich-exporter"
    static_configs:
      - targets: ["immich-exporter:9700"] # or your host/IP
        labels:
          host: "immich"
          service: "immich-exporter"
    scrape_interval: 60s
    scrape_timeout: 30s
```

## CI/CD

- Forgejo Actions (`.forgejo/workflows/build.yml`, runner `ci-runner`) builds `linux/amd64` on every push to `main` and every pull request. It is a build-only source gate and publishes nothing.
- Images are published to the Forgejo registry by an owner-approved exact-SHA dispatch in the private `johnny/registry-publishers` repo (recipe `immich-prometheus-exporter`; an optional stable `vX.Y.Z` tag at the same `main` commit is passed as `release_tag`). Pushing a tag here no longer builds or publishes an image.
- The repo is hosted on Forgejo and push-mirrored to GitHub. GHCR is no longer published to; the existing `ghcr.io/kryptionx/immich-prometheus-exporter` tags are frozen legacy copies.

## License

MIT
