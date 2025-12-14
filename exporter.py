#!/usr/bin/env python3
"""
Immich Prometheus Exporter
Queries Immich API and exposes metrics for Prometheus

Based on: finkregh/immich-prometheus-exporter
"""

import os
import time
import logging
from typing import Dict, Any, List
import requests
from prometheus_client import start_http_server, Gauge, Info, Counter

# Configuration
IMMICH_URL = os.getenv('IMMICH_URL', 'http://localhost:2283')
IMMICH_API_KEY = os.getenv('IMMICH_API_KEY')
EXPORTER_PORT = int(os.getenv('EXPORTER_PORT', '9700'))
SCRAPE_INTERVAL = int(os.getenv('SCRAPE_INTERVAL', '60'))

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Prometheus Metrics
immich_up = Gauge('immich_up', 'Immich server is up (1) or down (0)')
immich_server_version = Info('immich_server', 'Immich server version information')

# User metrics
immich_user_total_assets = Gauge(
    'immich_user_total_assets',
    'Total number of assets per user',
    ['user_id', 'user_name']
)
immich_user_images_count = Gauge(
    'immich_user_images_count',
    'Number of images per user',
    ['user_id', 'user_name']
)
immich_user_videos_count = Gauge(
    'immich_user_videos_count',
    'Number of videos per user',
    ['user_id', 'user_name']
)
immich_user_quota_bytes = Gauge(
    'immich_user_quota_bytes',
    'User quota in bytes',
    ['user_id', 'user_name']
)
immich_user_quota_usage_bytes = Gauge(
    'immich_user_quota_usage_bytes',
    'User quota usage in bytes',
    ['user_id', 'user_name']
)

# Album metrics
immich_album_count = Gauge(
    'immich_album_count',
    'Number of albums',
    ['user_id', 'user_name', 'album_type']
)

# Server statistics
immich_server_photos_total = Gauge('immich_server_photos_total', 'Total number of photos on server')
immich_server_videos_total = Gauge('immich_server_videos_total', 'Total number of videos on server')
immich_server_usage_bytes = Gauge('immich_server_usage_bytes', 'Total storage usage in bytes')
immich_server_users_total = Gauge('immich_server_users_total', 'Total number of users')

# Error counter
immich_scrape_errors_total = Counter('immich_scrape_errors_total', 'Total number of scrape errors')


class ImmichClient:
    """Client for Immich API"""
    
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({
            'x-api-key': api_key,
            'Accept': 'application/json'
        })
    
    def _request(self, method: str, endpoint: str, **kwargs) -> Any:
        """Make HTTP request to Immich API"""
        url = f"{self.base_url}{endpoint}"
        try:
            response = self.session.request(method, url, timeout=30, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {method} {endpoint} - {e}")
            raise
    
    def get_server_version(self) -> Dict[str, Any]:
        """Get server version information"""
        return self._request('GET', '/api/server/version')
    
    def get_server_statistics(self) -> Dict[str, Any]:
        """Get server statistics"""
        return self._request('GET', '/api/server/statistics')
    
    def get_users(self) -> List[Dict[str, Any]]:
        """Get list of all users"""
        return self._request('GET', '/api/users')
    
    def get_user_statistics(self, user_id: str) -> Dict[str, Any]:
        """Get statistics for a specific user"""
        return self._request('GET', f'/api/users/{user_id}/statistics')
    
    def get_albums(self) -> List[Dict[str, Any]]:
        """Get list of all albums"""
        return self._request('GET', '/api/albums')


def collect_metrics(client: ImmichClient):
    """Collect all metrics from Immich"""
    try:
        # Server version
        logger.info("Collecting server version...")
        try:
            version_info = client.get_server_version()
            immich_server_version.info({
                'version': version_info.get('version', 'unknown'),
                'major': str(version_info.get('major', '0')),
                'minor': str(version_info.get('minor', '0')),
                'patch': str(version_info.get('patch', '0'))
            })
            immich_up.set(1)
        except Exception as e:
            logger.error(f"Failed to get server version: {e}")
            immich_up.set(0)
            immich_scrape_errors_total.inc()
            return
        
        # Server statistics
        logger.info("Collecting server statistics...")
        try:
            stats = client.get_server_statistics()
            immich_server_photos_total.set(stats.get('photos', 0))
            immich_server_videos_total.set(stats.get('videos', 0))
            immich_server_usage_bytes.set(stats.get('usage', 0))
            immich_server_users_total.set(stats.get('usageByUser', [{}]).__len__())
        except Exception as e:
            logger.warning(f"Failed to get server statistics: {e}")
            immich_scrape_errors_total.inc()
        
        # User information and statistics
        logger.info("Collecting user statistics...")
        try:
            users = client.get_users()
            logger.info(f"Found {len(users)} users")
            
            for user in users:
                user_id = user.get('id')
                user_name = user.get('name', user.get('email', 'unknown'))
                
                try:
                    # Get user statistics
                    user_stats = client.get_user_statistics(user_id)
                    
                    # Extract metrics
                    images = user_stats.get('images', 0)
                    videos = user_stats.get('videos', 0)
                    total_assets = images + videos
                    usage = user_stats.get('usage', 0)
                    quota = user_stats.get('quota', 0)
                    
                    # Set metrics
                    immich_user_total_assets.labels(user_id=user_id, user_name=user_name).set(total_assets)
                    immich_user_images_count.labels(user_id=user_id, user_name=user_name).set(images)
                    immich_user_videos_count.labels(user_id=user_id, user_name=user_name).set(videos)
                    immich_user_quota_bytes.labels(user_id=user_id, user_name=user_name).set(quota)
                    immich_user_quota_usage_bytes.labels(user_id=user_id, user_name=user_name).set(usage)
                    
                    logger.debug(f"User {user_name}: {images} images, {videos} videos, {usage} bytes used")
                    
                except Exception as e:
                    logger.warning(f"Failed to get statistics for user {user_name}: {e}")
                    immich_scrape_errors_total.inc()
        
        except Exception as e:
            logger.error(f"Failed to get users: {e}")
            immich_scrape_errors_total.inc()
        
        # Album information
        logger.info("Collecting album information...")
        try:
            albums = client.get_albums()
            logger.info(f"Found {len(albums)} albums")
            
            # Count albums by user and type
            album_counts = {}
            for album in albums:
                owner_id = album.get('ownerId')
                owner_name = album.get('ownerName', 'unknown')
                is_shared = album.get('shared', False)
                album_type = 'shared' if is_shared else 'owned'
                
                key = (owner_id, owner_name, album_type)
                album_counts[key] = album_counts.get(key, 0) + 1
            
            # Set metrics
            for (owner_id, owner_name, album_type), count in album_counts.items():
                immich_album_count.labels(
                    user_id=owner_id,
                    user_name=owner_name,
                    album_type=album_type
                ).set(count)
                logger.debug(f"User {owner_name}: {count} {album_type} albums")
        
        except Exception as e:
            logger.warning(f"Failed to get albums: {e}")
            immich_scrape_errors_total.inc()
        
        logger.info("Metrics collection complete")
    
    except Exception as e:
        logger.error(f"Unexpected error during metrics collection: {e}")
        immich_up.set(0)
        immich_scrape_errors_total.inc()


def main():
    """Main exporter loop"""
    # Validate configuration
    if not IMMICH_API_KEY:
        logger.error("IMMICH_API_KEY environment variable is required!")
        exit(1)
    
    logger.info(f"Starting Immich Prometheus Exporter")
    logger.info(f"Immich URL: {IMMICH_URL}")
    logger.info(f"Exporter port: {EXPORTER_PORT}")
    logger.info(f"Scrape interval: {SCRAPE_INTERVAL}s")
    
    # Initialize client
    client = ImmichClient(IMMICH_URL, IMMICH_API_KEY)
    
    # Start HTTP server for Prometheus
    start_http_server(EXPORTER_PORT)
    logger.info(f"Metrics server started on port {EXPORTER_PORT}")
    logger.info(f"Metrics endpoint: http://localhost:{EXPORTER_PORT}/metrics")
    
    # Main loop
    while True:
        try:
            collect_metrics(client)
        except Exception as e:
            logger.error(f"Error in main loop: {e}")
        
        logger.info(f"Waiting {SCRAPE_INTERVAL}s until next scrape...")
        time.sleep(SCRAPE_INTERVAL)


if __name__ == '__main__':
    main()

