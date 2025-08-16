from pandas import DataFrame
from database.connection import db_manager


@db_manager.db_operation(autocommit=True, dict_cursor=True)
def extract_touch_points_data(conn, cursor) -> DataFrame:
    query = """
    WITH ordered_events AS (
    SELECT 
        user_id,
        campaign,
        platform,
        touchpoint_type,
        timestamp,
        ROW_NUMBER() OVER (PARTITION BY user_id, campaign, platform ORDER BY timestamp) as rn
    FROM events
)
SELECT 
    user_id,
    campaign,
    platform,
    MIN(CASE WHEN touchpoint_type = 'impression' THEN timestamp END) AS impression_time,
    MIN(CASE WHEN touchpoint_type = 'view' THEN timestamp END) AS view_time,
    MIN(CASE WHEN touchpoint_type = 'click' THEN timestamp END) AS click_time,
    (MIN(CASE WHEN touchpoint_type = 'view' THEN timestamp END) - 
     MIN(CASE WHEN touchpoint_type = 'impression' THEN timestamp END)) AS time_to_view,
    (MIN(CASE WHEN touchpoint_type = 'click' THEN timestamp END) - 
     MIN(CASE WHEN touchpoint_type = 'view' THEN timestamp END)) AS time_to_click,
    (MIN(CASE WHEN touchpoint_type = 'click' THEN timestamp END) - 
     MIN(CASE WHEN touchpoint_type = 'impression' THEN timestamp END)) AS total_time_to_conversion
FROM ordered_events
GROUP BY user_id, campaign, platform;

    """
    cursor.execute(query)
    return DataFrame(cursor.fetchall())

