# ShipppingServiceRepo# ShippingService

## Overview

The **Shipping Service** is a core microservice within the ECI e-commerce platform. Its primary responsibility is to manage the logistics and shipment lifecycle for customer orders. This includes receiving shipment requests from the Order Service, coordinating with inventory and payment services, updating shipment status, and tracking deliveries.

Key features of the Shipping Service:
- Handles new shipment creation when orders are placed and paid.
- Tracks the status of each shipment from creation to delivery.
- Provides APIs for querying shipment information and current status.
- Integrates with inventory and order microservices to ensure end-to-end fulfillment.
- Exposes operational and business metrics for monitoring.

## Table of Contents

- [Overview](#overview)
- [Project Structure](#project-structure)
- [Tech Stack](#tech-stack)
- [API End Points (Quick)](#api-end-pointsquick)
- [Running the Service](#running-the-service)
  - [Local Environment](#local-environment)
  - [Docker (recommended)](#docker-recommended)
  - [Kubernetes Deployment & Prometheus Setup](#kubernetes-deployment--prometheus-setup)
- [Database Schema](#database-scehema)
- [Contact](#contact)


## Project Structure
```
ShippingServiceRepo/
│
├── .gitignore
├── Dockerfile
├── docker-compose.yml
├── docker-entrypoint.sh
├── requirements.txt
├── init.sql
├── seed_db.py
│
├── k8s/
│   ├── prometheus/
│   ├── deployment.yaml
│   ├── postgres.yaml
│   ├── service.yaml
│
├── ShippingService/
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── __init__.py
│
├── shippingapp/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── metrics.py
│   ├── models.py
│   ├── serializers.py
│   ├── tests.py
│   ├── views.py
│   ├── migrations/
│   ├── static/
│   ├── Status/
│   └── Service/
│        ├── inventory_client.py
│        └── order_client.py
│
├── SeedData/
│   └── eci_shipments.csv
│
├── manage.py
```

## Tech Stack
| Layer          | Technology / Tool             | Description                     |
| -------------- | ----------------------------- | ------------------------------- |
| Language       | Python 3.12                   | Core service development        |
| Framework      | Django, Django REST Framework | Web API, business logic         |
| Database       | PostgreSQL                    | Persistent storage              |
| Container      | Docker, docker-compose        | Application containerization    |
| Orchestration  | Kubernetes                    | Cluster deployment & management |
| Monitoring     | Prometheus                    | Metrics and monitoring          |
| Dev Tools      | VSCode, PyCharm               | IDEs for development            |
| Source Control | Git                           | Version control                 |

## API End Points(Quick)
| Endpoint               | Method | Purpose / Description                                | Example Path          |
| ---------------------- | ------ | ---------------------------------------------------- | --------------------- |
| /health                | GET    | Basic liveness probe, returns service status         | /health               |
| /readiness             | GET    | Readiness probe, checks DB connectivity              | /readiness            |
| /shipments/create      | POST   | Create a new shipment for a confirmed order          | /shipments/create     |
| /shipments/{id}/update | PATCH  | Update status of a shipment (e.g. PENDING → SHIPPED) | /shipments/123/update |
| /shipments/{id}        | GET    | Get shipment details by Shipment ID                  | /shipments/123        |
| /metrics               | GET    | Prometheus metrics endpoint                          | /metrics              |

## Running the Service
### Local Environment
```bash
# 1. Create & activate virtual environment
python -m venv venv
source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set up .env file as above

# 4. Create database tables
python manage.py migrate

# 5. (Optional) Seed sample data
python seed_db.py

# 6. Start service
python manage.py runserver 0.0.0.0:8001
# Or (for production):
gunicorn OrderService.wsgi:application --bind 0.0.0.0:8001
```

## Docker (recommended)

```bash
# Build and run containers for OrderService and Postgres
docker compose up --build

# Stop all containers
docker compose down

# Remove containers & volumes
docker compose down -v

# Rebuild after code/dependency changes
docker compose up --build

# See service status
docker ps

# The API is available at http://localhost:8001/

```

## Kubernetes Deployment & Prometheus Setup

```bash
# Start local cluster
minikube start

# (Optional) Enable ingress
minikube addons enable ingress

# Deploy database
kubectl apply -f k8s/postgres-deployment.yaml

# Deploy OrderService
kubectl apply -f k8s/order-service-configmap.yaml
kubectl apply -f k8s/order-service-deployment.yaml

# Deploy monitoring
kubectl apply -f k8s/prometheus-configmap.yaml
kubectl apply -f k8s/prometheus-deployment.yaml
kubectl apply -f k8s/prometheus-service.yaml

# List pods/services
kubectl get pods
kubectl get svc

# Access OrderService or Prometheus dashboards
minikube service order-service
minikube service prometheus

# Stop and remove cluster
minikube stop
minikube delete

```

## Database Scehema
```sql
CREATE TABLE IF NOT EXISTS public.shippingapp_shipment (
    shipment_id integer NOT NULL GENERATED BY DEFAULT AS IDENTITY (
        INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 2147483647 CACHE 1
    ),
    order_id integer NOT NULL,
    carrier character varying(100) NOT NULL,
    tracking_no character varying(100) NOT NULL,
    status character varying(20) NOT NULL,
    shipped_at timestamp with time zone,
    delivered_at timestamp with time zone,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL,
    CONSTRAINT shippingapp_shipment_pkey PRIMARY KEY (shipment_id),
    CONSTRAINT shippingapp_shipment_tracking_no_key UNIQUE (tracking_no)
);
```
## Contact

- P Naveen Prabhath | 2024tm93544@wilp.bits-pilani.ac.in
