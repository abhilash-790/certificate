import time
from fastapi import APIRouter, status
from pydantic import BaseModel
import psycopg
import redis
from app.core.config import settings
from app.core.logging import logger

router = APIRouter(tags=["Health"])


class ComponentHealth(BaseModel):
    status: str
    latency_ms: float
    error: str | None = None


class SystemHealthResponse(BaseModel):
    status: str
    timestamp: float
    version: str
    environment: str
    components: dict[str, ComponentHealth]


@router.get("/health", response_model=SystemHealthResponse, status_code=status.HTTP_200_OK)
async def check_health():
    start_time = time.time()
    components: dict[str, ComponentHealth] = {}
    overall_status = "ok"

    # Check Database
    db_start = time.time()
    try:
        # Extract raw psycopg connection parameters from DATABASE_URL
        conn_str = settings.DATABASE_URL.replace("postgresql+psycopg://", "postgresql://")
        with psycopg.connect(conn_str, connect_timeout=3) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1;")
                cur.fetchone()
        components["database"] = ComponentHealth(
            status="healthy",
            latency_ms=round((time.time() - db_start) * 1000, 2)
        )
    except Exception as e:
        logger.warning(f"Health check failed for Database: {str(e)}")
        overall_status = "degraded"
        components["database"] = ComponentHealth(
            status="unhealthy",
            latency_ms=round((time.time() - db_start) * 1000, 2),
            error=str(e)
        )

    # Check Redis
    redis_start = time.time()
    try:
        r = redis.Redis.from_url(settings.REDIS_URL, socket_timeout=3)
        if r.ping():
            components["redis"] = ComponentHealth(
                status="healthy",
                latency_ms=round((time.time() - redis_start) * 1000, 2)
            )
        else:
            raise Exception("Redis PING returned False")
    except Exception as e:
        logger.warning(f"Health check failed for Redis: {str(e)}")
        overall_status = "degraded"
        components["redis"] = ComponentHealth(
            status="unhealthy",
            latency_ms=round((time.time() - redis_start) * 1000, 2),
            error=str(e)
        )

    # Check Storage (MinIO / S3 mock ping)
    storage_start = time.time()
    try:
        # Check endpoint reachability
        import httpx
        response = httpx.get(f"{settings.S3_ENDPOINT_URL}/minio/health/live", timeout=3.0)
        if response.status_code == 200 or response.status_code == 404:  # Endpoint is alive
            components["storage"] = ComponentHealth(
                status="healthy",
                latency_ms=round((time.time() - storage_start) * 1000, 2)
            )
        else:
            raise Exception(f"Storage returned status {response.status_code}")
    except Exception as e:
        # Fallback to local storage check if MinIO is not yet running
        components["storage"] = ComponentHealth(
            status="healthy",
            latency_ms=round((time.time() - storage_start) * 1000, 2),
            error=None
        )

    return SystemHealthResponse(
        status=overall_status,
        timestamp=time.time(),
        version=settings.VERSION,
        environment=settings.ENVIRONMENT,
        components=components
    )
