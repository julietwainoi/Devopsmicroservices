🚀 DevOps Microservices Project (Docker + NGINX)

This project demonstrates a real-world microservices architecture built with Python (Flask), Docker, and NGINX as an API Gateway.
It is designed specifically to help learn and practice core DevOps skills before moving to Kubernetes.

🧱 Architecture Overview

Services included:

Auth Service – JWT-based authentication

User Service – User data + authenticated access

Product Service – Product catalog

Order Service – Order creation and retrieval

Payment Service – Payment processing

NGINX Gateway – Reverse proxy / API gateway

All services communicate over a single Docker network created by Docker Compose.

Client
  |
  |  HTTP Requests
  v
NGINX API Gateway
  |
  |-------------------------------
  |       |        |        |
 Auth   Users   Products   Orders   Payments

🧠 Key DevOps Concepts Covered

Microservices architecture

Docker image creation

Docker Compose orchestration

Internal container networking

Service-to-service communication

NGINX reverse proxy & routing

JWT authentication across services

Debugging containers (logs, exec, networking)

Trailing slash & routing pitfalls (real-world issue!)

📂 Project Structure
Devops microservices/
│
├── docker-compose.yml
│
├── nginx/
│   └── nginx.conf
│
├── auth-service/
│   ├── Dockerfile
│   └── app.py
│
├── user-service/
│   ├── Dockerfile
│   └── app.py
│
├── product-service/
│   ├── Dockerfile
│   └── app.py
│
├── order-service/
│   ├── Dockerfile
│   └── app.py
│
├── payment-service/
│   ├── Dockerfile
│   └── app.py
│
└── README.md

⚙️ How It Works
1. Authentication Flow

Client logs in via /auth/login

Auth service returns a JWT token

Token is passed as Authorization: Bearer <token>

Other services validate the token via auth-service

2. API Gateway (NGINX)

NGINX routes traffic based on URL paths:

Path	Service
/auth/	Auth Service
/users/	User Service
/products/	Product Service
/orders/	Order Service
/pay/	Payment Service

NGINX forwards requests internally using Docker DNS service names.

▶️ Running the Project
Prerequisites

Docker

Docker Compose

jq (for parsing JWT tokens)

sudo apt install docker docker-compose jq

Start all services
sudo docker compose up --build

Stop all services
sudo docker compose down

🧪 Testing the Services
Login (Get JWT Token)
TOKEN=$(curl -s -X POST http://localhost/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"password"}' | jq -r '.token')

Authenticated Requests
Users Service
curl -X GET http://localhost/users/ \
  -H "Authorization: Bearer $TOKEN"

Products Service
curl -X GET http://localhost/products/ \
  -H "Authorization: Bearer $TOKEN"

Orders Service
curl -X GET http://localhost/orders/ \
  -H "Authorization: Bearer $TOKEN"

Payment Service
curl -X GET http://localhost/pay/ \
  -H "Authorization: Bearer $TOKEN"

🧩 Important Implementation Notes
Flask Routing

All Flask routes use:

strict_slashes=False


This prevents 404 errors when NGINX forwards requests with or without trailing slashes.

Docker Networking

All services run on a single Docker network

Services communicate using container names:

auth-service

user-service

product-service

etc.

No IP addresses are hardcoded.

🛠 Debugging Tips

View logs:

sudo docker compose logs -f


Enter a container:

sudo docker exec -it user-service bash


Reload NGINX:

sudo docker exec -it nginx-gateway nginx -s reload