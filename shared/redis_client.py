import os
import redis

_redis_client = None

def get_redis_connection() -> redis.Redis:
    """
    Exposes an Upstash Redis connection client.
    """
    global _redis_client
    if _redis_client is None:
        host = os.getenv("REDIS_HOST", "")
        port_str = os.getenv("REDIS_PORT", "6379")
        password = os.getenv("REDIS_PASSWORD", "")
        ssl_str = os.getenv("REDIS_SSL", "true")
        
        # Clean quotes
        if host.startswith('"') and host.endswith('"'):
            host = host[1:-1]
        if password.startswith('"') and password.endswith('"'):
            password = password[1:-1]
            
        try:
            port = int(port_str)
        except ValueError:
            port = 6379
            
        ssl = ssl_str.lower() in ("true", "1", "yes")
        
        _redis_client = redis.Redis(
            host=host,
            port=port,
            username="default",
            password=password,
            ssl=ssl,
            ssl_cert_reqs=None, # Avoid SSL certificate verification issues for serverless redis
            decode_responses=True,
            socket_timeout=5.0
        )
    return _redis_client


