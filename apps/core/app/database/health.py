"""Database health checks."""

import structlog
from sqlalchemy import text

from app.database.session import engine

logger = structlog.get_logger(__name__)


async def check_database_health() -> dict:
    """Check database health."""
    try:
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT 1"))
            result.fetchone()

        return {
            "status": "healthy",
            "message": "Database connection successful"
        }
    except Exception as e:
        logger.error("Database health check failed", error=str(e))
        return {
            "status": "unhealthy",
            "message": f"Database connection failed: {str(e)}"
        }


async def check_database_performance() -> dict:
    """Check database performance metrics."""
    try:
        async with engine.connect() as conn:
            # Check connection pool status
            pool_status = engine.pool.status()

            # Check query performance
            result = await conn.execute(text(
                "SELECT pg_stat_database.datname, "
                "pg_stat_database.numbackends, "
                "pg_stat_database.xact_commit, "
                "pg_stat_database.xact_rollback "
                "FROM pg_stat_database "
                "WHERE pg_stat_database.datname = current_database()"
            ))
            db_stats = result.fetchone()

            return {
                "status": "healthy",
                "pool_size": pool_status.size,
                "pool_checked_out": pool_status.checkedout,
                "pool_overflow": pool_status.overflow,
                "num_backends": db_stats[1] if db_stats else 0,
                "commits": db_stats[2] if db_stats else 0,
                "rollbacks": db_stats[3] if db_stats else 0,
            }
    except Exception as e:
        logger.error("Database performance check failed", error=str(e))
        return {
            "status": "unhealthy",
            "message": f"Performance check failed: {str(e)}"
        }


async def check_table_sizes() -> dict:
    """Check table sizes for monitoring."""
    try:
        async with engine.connect() as conn:
            result = await conn.execute(text(
                "SELECT "
                "schemaname, "
                "tablename, "
                "pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size "
                "FROM pg_tables "
                "WHERE schemaname = 'public' "
                "ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC"
            ))
            table_sizes = result.fetchall()

            return {
                "status": "healthy",
                "tables": [
                    {"schema": row[0], "table": row[1], "size": row[2]}
                    for row in table_sizes
                ]
            }
    except Exception as e:
        logger.error("Table size check failed", error=str(e))
        return {
            "status": "unhealthy",
            "message": f"Table size check failed: {str(e)}"
        }


async def check_index_usage() -> dict:
    """Check index usage for optimization."""
    try:
        async with engine.connect() as conn:
            result = await conn.execute(text(
                "SELECT "
                "schemaname, "
                "tablename, "
                "indexname, "
                "idx_tup_read, "
                "idx_tup_fetch "
                "FROM pg_stat_user_indexes "
                "ORDER BY idx_tup_read DESC "
                "LIMIT 20"
            ))
            index_stats = result.fetchall()

            return {
                "status": "healthy",
                "indexes": [
                    {
                        "schema": row[0],
                        "table": row[1],
                        "index": row[2],
                        "tuples_read": row[3],
                        "tuples_fetched": row[4],
                    }
                    for row in index_stats
                ]
            }
    except Exception as e:
        logger.error("Index usage check failed", error=str(e))
        return {
            "status": "unhealthy",
            "message": f"Index usage check failed: {str(e)}"
        }
