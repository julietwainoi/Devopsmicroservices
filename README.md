🧩 DevOps Microservices Project

This project is a Docker Compose–based microservices architecture built with Flask, PostgreSQL, and Nginx.
It demonstrates service-to-service communication, API gateway routing, database persistence, and schema-based PostgreSQL design.

🏗️ Architecture Overview

The system consists of five microservices, an API gateway, and a PostgreSQL database:

Client
  |
  v
Nginx (API Gateway)
  |
  +--> Auth Service
  +--> User Service
  +--> Product Service
  +--> Order Service --> PostgreSQL
  +--> Payment Service

Services
Service	Description
nginx	API Gateway that routes requests to backend services
auth-service	Handles authentication and token validation
user-service	Manages users
product-service	Provides product data
order-service	Creates orders and stores them in PostgreSQL
payment-service	Simulates payment processing
order-db	PostgreSQL database for orders
🧰 Tech Stack

Python (Flask)

PostgreSQL 16

Docker & Docker Compose

Nginx

psycopg2

JSONB (PostgreSQL)

📁 Project Structure
.
├── docker-compose.yml
├── nginx/
│   └── nginx.conf
├── auth-service/
├── user-service/
├── product-service/
├── order-service/
│   ├── app.py
│   ├── db.py
│   └── Dockerfile
├── payment-service/
├── order-db-services/
│   └── init/
│       └── 01-create-orders.sql
└── README.md

🗄️ Database Design

Database: orders_user

Schema: orders

Table: orders.orders

CREATE SCHEMA IF NOT EXISTS orders;

CREATE TABLE IF NOT EXISTS orders.orders (
    id SERIAL PRIMARY KEY,
    product JSONB NOT NULL,
    status VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


ℹ️ The SQL scripts in /docker-entrypoint-initdb.d run only when the database volume is empty.

� Docker Compose Configuration

All services run on a shared Docker bridge network: micro-net

PostgreSQL data is persisted using a named volume: order_db_data

Nginx exposes port 80

PostgreSQL is exposed on port 5433

▶️ Running the Project
1️⃣ Build and start all services
sudo docker compose up -d --build

2️⃣ Verify running containers
sudo docker compose ps

🔄 Rebuilding a Single Service

If you change code in order-service:

sudo docker compose up -d --build order-service

🧹 Resetting the Database (Fresh Start)

To completely reset PostgreSQL (schemas + tables):

sudo docker compose down
sudo docker volume rm devopsmicroservices_order_db_data
sudo docker compose up -d order-db
sudo docker compose up -d


⚠️ This deletes all persisted database data.

🔍 Inspecting the Database
Access PostgreSQL shell
sudo docker exec -it order-db psql -U orders_user -d orders_user

Useful commands inside psql
\dn                 -- list schemas
\dt orders.*        -- list tables in orders schema
\d orders.orders    -- describe table


 TOKEN=$(curl -s -X POST http://microservices.local/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"password"}' | jq -r '.token')

curl -X POST http://microservices.local/orders/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"product_id": 1}'

curl -X POST http://microservices.local/payments/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"amount": 100}'

🧠 Key Concepts Demonstrated

Docker networking and service discovery

API Gateway pattern

PostgreSQL schemas (orders.orders)

Persistent volumes

Health checks

JSONB storage

Microservice-to-microservice communication

🚀 Future Improvements

Add migrations (Alembic/Flyway)

Centralized logging

Distributed tracing

Kubernetes deployment

CI/CD pipeline

👩‍💻 Author

Juliet
DevOps & Backend Microservices Project