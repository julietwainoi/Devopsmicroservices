import psycopg2
import os


def get_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "order-db"),
        database=os.getenv("DB_NAME", "orders"),
        user=os.getenv("DB_USER", "orders_user"),
        password=os.getenv("DB_PASS", "orders_pass"),
    )

