"""Queue health monitoring."""

from typing import Dict
from app.workers.celery_app import celery_app
import structlog

logger = structlog.get_logger(__name__)


async def check_queue_health() -> Dict:
    """Check Celery queue health."""
    try:
        inspect = celery_app.control.inspect()
        
        # Check active workers
        active_workers = inspect.active()
        if active_workers is None:
            active_workers = {}
        
        # Check scheduled tasks
        scheduled = inspect.scheduled()
        if scheduled is None:
            scheduled = {}
        
        # Check reserved tasks
        reserved = inspect.reserved()
        if reserved is None:
            reserved = {}
        
        # Calculate metrics
        total_active_tasks = sum(len(tasks) for tasks in active_workers.values())
        total_scheduled_tasks = sum(len(tasks) for tasks in scheduled.values())
        total_reserved_tasks = sum(len(tasks) for tasks in reserved.values())
        worker_count = len(active_workers)
        
        return {
            "status": "healthy",
            "worker_count": worker_count,
            "active_tasks": total_active_tasks,
            "scheduled_tasks": total_scheduled_tasks,
            "reserved_tasks": total_reserved_tasks,
            "workers": list(active_workers.keys()),
        }
    
    except Exception as e:
        logger.error("Queue health check failed", error=str(e))
        return {
            "status": "unhealthy",
            "message": f"Queue health check failed: {str(e)}"
        }


async def get_queue_stats(queue_name: str) -> Dict:
    """Get statistics for a specific queue."""
    try:
        with celery_app.connection_or_acquire() as conn:
            with conn.channel() as channel:
                # Get queue info
                queue_info = channel.queue_declare(queue_name, passive=True)
                
                return {
                    "queue": queue_name,
                    "message_count": queue_info.message_count,
                    "consumer_count": queue_info.consumer_count,
                    "status": "healthy",
                }
    
    except Exception as e:
        logger.error("Queue stats failed", queue=queue_name, error=str(e))
        return {
            "queue": queue_name,
            "status": "unhealthy",
            "message": f"Failed to get stats: {str(e)}"
        }


async def get_worker_stats() -> Dict:
    """Get worker statistics."""
    try:
        inspect = celery_app.control.inspect()
        
        # Get worker stats
        stats = inspect.stats()
        if stats is None:
            stats = {}
        
        # Get registered tasks
        registered = inspect.registered()
        if registered is None:
            registered = {}
        
        return {
            "status": "healthy",
            "workers": stats,
            "registered_tasks": registered,
        }
    
    except Exception as e:
        logger.error("Worker stats failed", error=str(e))
        return {
            "status": "unhealthy",
            "message": f"Worker stats failed: {str(e)}"
        }


async def purge_queue(queue_name: str) -> Dict:
    """Purge all messages from a queue."""
    try:
        with celery_app.connection_or_acquire() as conn:
            with conn.channel() as channel:
                result = channel.queue_purge(queue_name)
                
                logger.info("Queue purged", queue=queue_name, message_count=result)
                
                return {
                    "queue": queue_name,
                    "purged_count": result,
                    "status": "success",
                }
    
    except Exception as e:
        logger.error("Queue purge failed", queue=queue_name, error=str(e))
        return {
            "queue": queue_name,
            "status": "failed",
            "message": f"Purge failed: {str(e)}"
        }
