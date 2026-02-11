import psycopg2
from psycopg2.extras import Json

def get_connection():
    conn = psycopg2.connect(
        host="order-db",
        database="orders_user",
        user="orders_user",
        password="orders_pass"
    )
    # Set the default search_path
    with conn.cursor() as cur:
        cur.execute("SET search_path TO orders, public;")
    return conn
