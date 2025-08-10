import psycopg2

from config.config import DB_CONFIG

try:
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    cursor.execute('''SELECT COUNT(*) FROM campaigns;''')
    print("database connection established")
    conn.close()
except Exception as e:
    print(f"database connection failed with exception: {e}")
