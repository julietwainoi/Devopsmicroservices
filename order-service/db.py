import os
import psycopg2

def get_connection():
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST", "order-db"),
        database=os.getenv("DB_NAME", "orders_user"),
        user=os.getenv("DB_USER", "orders_user"),
        password=os.getenv("DB_PASS", "orders_pass")
    )
    with conn.cursor() as cur:
        cur.execute("SET search_path TO orders, public;")
    return conn
