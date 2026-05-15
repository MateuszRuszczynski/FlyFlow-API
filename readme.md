# ✈️ FlyFlow API

[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-6.0-green.svg)](https://www.djangoproject.com/)
[![Docker](https://img.shields.io/badge/Docker-Enabled-blue.svg)](https://www.docker.com/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

**FlyFlow** is an Airport Management System. It provides a comprehensive suite of tools for airline logistics, including flight scheduling, airplane tracking, and secure passenger data management.

---

## 🚀 Key Features

* **🔐 Secure Auth**: Full JWT implementation for user registration and profile management.
* **📡 Live API Docs**: Interactive Swagger and Redoc documentation generated automatically.
* **🏗️ Advanced Logistics**: Manage complex relationships between Airplanes, Routes, and Crews.
* **📦 Containerized**: One-command setup using Docker and Docker Compose.
* **🧪 High Coverage**: Over 44+ automated tests ensuring system stability.

---

## 🛠 Tech Stack

| Technology | Usage |
| :--- | :--- |
| **Django REST Framework** | Core API Logic |
| **PostgreSQL** | Relational Database |
| **SimpleJWT** | Authentication |
| **drf-spectacular** | API Documentation |
| **Ruff** | Fast Linting & Formatting |

---

## 🏁 Quick Start

### 1️⃣ Prerequisites
Ensure you have [Docker](https://www.docker.com/) installed on your local machine.

### 2️⃣ Installation
```bash
# Clone the repository
git clone https://github.com/MateuszRuszczynski/FlyFlow-API.git
cd flyflow_api

# Prepare environment variables
cp .env.sample .env
```
### 3️⃣ Build & Run
```bash
docker-compose up --build
```
The API will be run at http://localhost:8000

---

## ## 🛠 Tech Stack

## 📂 Project Architecture

| Folder / File | Description |
| :--- | :--- |
| **`airport/`** | The core application containing models, views, and logic for flights and airplanes. |
| **`users/`** | Manages the custom User model, authentication logic, and JWT endpoints. |
| **`flyflow_api/`** | The project's "brain" — contains global settings and root URL configuration. |
| **`requirements.txt`** | List of all Python dependencies required to run the project. |
| **`Dockerfile`** | Instructions for building the Django web container image. |
| **`docker-compose.yml`** | Orchestration file that links the Web and Database services together. |
| **`.env.sample`** | A template for environment variables to help others set up the project securely. |
