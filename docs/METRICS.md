# Metrics Reference

## Server Metrics
- `immich_server_photos_total`
- `immich_server_videos_total`
- `immich_server_usage_bytes`
- `immich_server_users_total`
- `immich_up`

## User Metrics
- `immich_user_total_assets{user_id, user_name}`
- `immich_user_images_count{user_id, user_name}`
- `immich_user_videos_count{user_id, user_name}`
- `immich_user_quota_bytes{user_id, user_name}`
- `immich_user_quota_usage_bytes{user_id, user_name}`

## Album Metrics
- `immich_album_count{user_id, user_name, album_type}`

## Labels
- `user_id`, `user_name`, `album_type` (owned|shared)
