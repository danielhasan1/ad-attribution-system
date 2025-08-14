import psycopg2
import psycopg2.extras
from contextlib import contextmanager
from functools import wraps
import logging
from typing import Optional, Dict, Any, List, Callable
from config.config import DB_CONFIG

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DatabaseManager:
    def __init__(self, db_config: Dict[str, Any]):
        self.db_config = db_config

    @contextmanager
    def get_connection(self, autocommit: bool = False):
        """Context manager for database connections"""
        conn = None
        try:
            conn = psycopg2.connect(**self.db_config)
            if autocommit:
                conn.autocommit = True
            logger.info("Database connection established")
            yield conn
        except psycopg2.Error as e:
            logger.error(f"Database error: {e}")
            if conn:
                conn.rollback()
            raise
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            if conn:
                conn.rollback()
            raise
        finally:
            if conn:
                conn.close()
                logger.info("Database connection closed")

    @contextmanager
    def get_cursor(self, autocommit: bool = False, dict_cursor: bool = False):
        """Context manager for database cursor"""
        with self.get_connection(autocommit=autocommit) as conn:
            cursor_factory = psycopg2.extras.DictCursor if dict_cursor else None
            cursor = conn.cursor(cursor_factory=cursor_factory)
            try:
                yield cursor, conn
            except Exception as e:
                conn.rollback()
                logger.error(f"Transaction rolled back due to: {e}")
                raise
            else:
                if not autocommit:
                    conn.commit()
                    logger.info("Transaction committed")
            finally:
                cursor.close()

    def db_operation(self, autocommit: bool = False, dict_cursor: bool = False):
        """Decorator for database operations"""

        def decorator(func: Callable):
            @wraps(func)
            def wrapper(*args, **kwargs):
                with self.get_cursor(autocommit=autocommit, dict_cursor=dict_cursor) as (cursor, conn):
                    return func(cursor, conn, *args, **kwargs)

            return wrapper

        return decorator

    def bulk_insert(self, table_name: str, data: List[Dict],
                    batch_size: int = 1000, on_conflict: str = "DO NOTHING"):
        """Optimized bulk insert using execute_values"""
        if not data:
            logger.warning("No data to insert")
            return 0

        # Get column names from first record
        columns = list(data[0].keys())
        column_str = ', '.join(columns)
        placeholders = ', '.join(['%s'] * len(columns))

        # SQL with ON CONFLICT handling
        sql = f"""
        INSERT INTO {table_name} ({column_str}) 
        VALUES %s 
        ON CONFLICT {on_conflict}
        """

        total_inserted = 0

        with self.get_cursor() as (cursor, conn):
            try:
                for i in range(0, len(data), batch_size):
                    batch = data[i:i + batch_size]
                    values = [tuple(row[col] for col in columns) for row in batch]

                    psycopg2.extras.execute_values(
                        cursor, sql, values, template=None, page_size=batch_size
                    )

                    batch_count = cursor.rowcount
                    total_inserted += batch_count
                    logger.info(f"Inserted batch {i // batch_size + 1}: {batch_count} records")

                logger.info(f"Total records inserted: {total_inserted}")
                return total_inserted

            except Exception as e:
                logger.error(f"Bulk insert failed: {e}")
                raise

db_manager = DatabaseManager(DB_CONFIG)



@db_manager.db_operation(autocommit=False, dict_cursor=True)
def load_campaign_data(cursor, conn, campaigns_df):
    """Load campaign data using decorated function"""

    data = campaigns_df.to_dict('records')

    # Using bulk insert
    return db_manager.bulk_insert('campaigns', data, batch_size=500)



def load_performance_data(performance_df):
    """Load performance data using context manager"""
    # Convert and bulk insert
    data = performance_df.to_dict('records')
    return db_manager.bulk_insert('daily_performance', data, batch_size=1000)


# Example 3: Data quality check decorator
# @db_manager.db_operation(dict_cursor=True)
# def data_quality_check(cursor, conn):
#     """Run data quality checks"""
#     checks = {}
#
#     # Check 1: Record counts
#     cursor.execute("SELECT COUNT(*) as campaign_count FROM campaigns")
#     checks['campaign_count'] = cursor.fetchone()['campaign_count']
#
#     cursor.execute("SELECT COUNT(*) as performance_count FROM facebook_performance")
#     checks['performance_count'] = cursor.fetchone()['performance_count']
#
#     # Check 2: Data integrity
#     cursor.execute("""
#         SELECT COUNT(*) as orphaned_records
#         FROM facebook_performance fp
#         LEFT JOIN campaigns c ON fp.campaign_id = c.campaign_id
#         WHERE c.campaign_id IS NULL
#     """)
#     checks['orphaned_records'] = cursor.fetchone()['orphaned_records']
#
#     # Check 3: Business logic validation
#     cursor.execute("""
#         SELECT COUNT(*) as invalid_spend
#         FROM facebook_performance
#         WHERE spend < 0 OR clicks < 0 OR impressions < 0
#     """)
#     checks['invalid_spend'] = cursor.fetchone()['invalid_spend']
#
#     return checks