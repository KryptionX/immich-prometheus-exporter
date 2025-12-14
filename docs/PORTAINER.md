# Portainer Deployment

Use `portainer-stack.yml` in the stack editor and set `IMMICH_API_KEY` in environment variables.

Steps:
1. Build automatically via GHCR (no local build)
2. In Portainer: Stacks → Add Stack → Web Editor
3. Paste `portainer-stack.yml`
4. Set `IMMICH_API_KEY` and `IMMICH_URL` in the UI
5. Deploy

Image: `ghcr.io/kryptionx/immich-prometheus-exporter:latest`
