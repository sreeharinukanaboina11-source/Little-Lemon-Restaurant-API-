# Little Lemon Restaurant Management API

**Coursera Meta Backend Developer Capstone Project**

A complete Django REST Framework backend application featuring menu management, table reservations with conflict validation, role-based access control, token authentication, automated unit testing, MySQL integration, static HTML rendering, and Insomnia client support.

---

## Peer-Review Mandatory Requirements Compliance

| # | Peer-Review Requirement | Implementation & Verification Status |
|---|---|---|
| 1 | **Django serves static HTML content** | **Verified**: Serves `templates/index.html` with Little Lemon branding and `static/css/style.css` at `/` and `/restaurant/`. |
| 2 | **Git repository on GitHub** | **Verified**: Committed to `https://github.com/sreeharinukanaboina11-source/Little-Lemon-Restaurant-API-.git` with `.gitignore` and clean tree. |
| 3 | **Connects to MySQL database** | **Verified**: Configured in `settings.py` with `pymysql` driver, `.env.example`, utf8mb4 encoding, and environment variable support. |
| 4 | **Menu APIs implemented correctly** | **Verified**: CRUD, category management, searching (`?search=`), filtering (`?category=`, `?to_price=`), ordering (`?ordering=`), pagination. |
| 5 | **Table-booking APIs implemented correctly** | **Verified**: `Booking` model with slot validation, overlapping conflict rejection, customer object-level authorization, and CRUD endpoints. |
| 6 | **User registration and authentication** | **Verified**: `POST /api/users/` (Registration), `POST /api-token-auth/` (Token login), secure permission classes. |
| 7 | **Automated unit tests pass** | **Verified**: 37 unit tests covering models, serializers, views, permissions, bookings, and conflicts. 100% passing (`OK`). |
| 8 | **Insomnia REST client testing** | **Verified**: Provided `Insomnia_LittleLemon_collection.json` importable collection and step-by-step instructions. |

---

## Quick Setup Guide

### 1. Prerequisites
- Python 3.10+ (tested on Python 3.14)
- MySQL Server 8.0+ (or MariaDB)
- Git

### 2. Clone and Setup Environment
```bash
git clone https://github.com/sreeharinukanaboina11-source/Little-Lemon-Restaurant-API-.git
cd Little-Lemon-Restaurant-API-
```

Create and activate virtual environment:
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

Install dependencies:
```bash
pip install -r requirements.txt
```

### 3. Database Configuration (MySQL)
Create database in MySQL:
```sql
CREATE DATABASE littlelemon CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

Copy `.env.example` to `.env` and fill in credentials:
```ini
DB_ENGINE=mysql
DB_NAME=littlelemon
DB_USER=root
DB_PASSWORD=your_password
DB_HOST=127.0.0.1
DB_PORT=3306
```
*(To run locally without MySQL, set `DB_ENGINE=sqlite`)*

Apply migrations & create initial groups:
```bash
python manage.py makemigrations restaurant
python manage.py migrate
python manage.py setup_groups
python manage.py createsuperuser
```

### 4. Run Server
```bash
python manage.py runserver
```

- Homepage: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- API Root: [http://127.0.0.1:8000/api/](http://127.0.0.1:8000/api/)
- Django Admin: [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)

---

## Automated Unit Testing

Run the full automated test suite:
```bash
python manage.py test -v 2
```
Output:
```
Ran 37 tests in 20.445s
OK
```

---

## API Endpoints Reference

### Authentication
| Method | Endpoint | Description | Access |
|---|---|---|---|
| `POST` | `/api/users/` | Register new customer | Public |
| `POST` | `/api-token-auth/` | Obtain auth token | Public |

Header for authenticated endpoints:
```http
Authorization: Token <your_token>
```

### Static Content
| Method | Endpoint | Description | Access |
|---|---|---|---|
| `GET` | `/` | Restaurant Homepage HTML | Public |
| `GET` | `/restaurant/` | Restaurant Homepage HTML (alias) | Public |

### Menu & Categories
| Method | Endpoint | Description | Access |
|---|---|---|---|
| `GET` | `/api/categories/` | List categories | Public |
| `POST` | `/api/categories/` | Create category | Admin |
| `GET` | `/api/menu-items/` | List / search / filter menu items | Public |
| `POST` | `/api/menu-items/` | Create menu item | Manager / Admin |
| `GET` | `/api/menu-items/{id}/` | Retrieve menu item | Public |
| `PUT/PATCH` | `/api/menu-items/{id}/` | Update menu item | Manager / Admin |
| `DELETE` | `/api/menu-items/{id}/` | Delete menu item | Manager / Admin |

### Table Bookings
| Method | Endpoint | Description | Access |
|---|---|---|---|
| `GET` | `/api/bookings/` | List bookings (own for customer, all for manager) | Authenticated |
| `POST` | `/api/bookings/` | Create booking (checks table & time conflicts) | Authenticated |
| `GET` | `/api/bookings/{id}/` | Retrieve booking | Owner / Manager |
| `PUT/PATCH` | `/api/bookings/{id}/` | Update booking | Owner / Manager |
| `DELETE` | `/api/bookings/{id}/` | Delete booking | Owner / Manager |

*Aliases supported: `/api/booking/tables/` and `/api/tables/`*

### Cart & Orders
| Method | Endpoint | Description | Access |
|---|---|---|---|
| `GET` | `/api/cart/menu-items/` | View current user's cart | Authenticated |
| `POST` | `/api/cart/menu-items/` | Add item to cart | Authenticated |
| `DELETE` | `/api/cart/menu-items/` | Clear cart | Authenticated |
| `POST` | `/api/orders/` | Checkout: create order from cart | Authenticated |
| `GET` | `/api/orders/` | List orders (role-based) | Authenticated |
| `GET` | `/api/orders/{id}/` | View order details | Permitted user |
| `PATCH` | `/api/orders/{id}/` | Update status / assign delivery crew | Manager / Crew |

### Role Management
| Method | Endpoint | Description | Access |
|---|---|---|---|
| `GET/POST/DELETE` | `/api/groups/manager/users/` | Manage Manager group members | Admin |
| `GET/POST/DELETE` | `/api/groups/delivery-crew/users/` | Manage Delivery crew members | Manager / Admin |

---

## Insomnia REST Testing

Import `Insomnia_LittleLemon_collection.json` directly into Insomnia:
1. Open Insomnia -> **Create** -> **Import From** -> **File**.
2. Select `Insomnia_LittleLemon_collection.json`.
3. Set `base_url` to `http://127.0.0.1:8000`.
4. Run requests in sequential order.
