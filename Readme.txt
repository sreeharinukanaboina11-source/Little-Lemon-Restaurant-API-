================================================================================
LITTLE LEMON RESTAURANT MANAGEMENT API
Coursera Backend Developer Capstone Project
================================================================================

1. PROJECT OVERVIEW
--------------------------------------------------------------------------------
Little Lemon Restaurant Management API is a production-ready Django REST Framework
application fulfilling all requirements of the Coursera Meta Backend Developer 
Capstone peer-review rubric.

Core Capabilities:
  - Django serves static HTML content for the Little Lemon restaurant homepage.
  - Full REST API with Menu item and Category management (CRUD, filtering, searching,
    ordering, pagination).
  - Robust Table Booking API with date/time/table validation, prevention of overlapping
    reservations, and object-level permissions.
  - Role-Based Access Control (Admin, Manager, Delivery crew, Customer).
  - Secure Token Authentication and User Registration.
  - Cart and Order placement pipeline.
  - MySQL database connectivity with environment variable configuration.
  - Automated unit test suite with 37 passing test cases.
  - Pre-configured Insomnia REST testing collection.


2. PREREQUISITES
--------------------------------------------------------------------------------
  - Python 3.10+ (tested on Python 3.14)
  - MySQL Server 8.0+ (or compatible MariaDB)
  - Git
  - (Optional) Insomnia REST Client for API testing


3. INSTALLATION & ENVIRONMENT SETUP
--------------------------------------------------------------------------------
Step 1: Clone the repository
    git clone https://github.com/sreeharinukanaboina11-source/Little-Lemon-Restaurant-API-.git
    cd Little-Lemon-Restaurant-API-

Step 2: Create a virtual environment
    Windows:
        python -m venv venv
        .\venv\Scripts\activate
    macOS / Linux:
        python3 -m venv venv
        source venv/bin/activate

Step 3: Install dependencies
    pip install -r requirements.txt


4. DATABASE CONFIGURATION (MySQL)
--------------------------------------------------------------------------------
Coursera Capstone Requirement: The backend connects to a MySQL database.

Step 1: Create the MySQL Database
    Open MySQL shell or MySQL Workbench and run:
        CREATE DATABASE littlelemon CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

Step 2: Configure Environment Variables
    Copy .env.example to .env:
        Windows:
            copy .env.example .env
        macOS / Linux:
            cp .env.example .env

    Update .env with your MySQL credentials:
        DB_ENGINE=mysql
        DB_NAME=littlelemon
        DB_USER=root
        DB_PASSWORD=your_mysql_password
        DB_HOST=127.0.0.1
        DB_PORT=3306

    Note: If MySQL is not running on your machine or for automated testing,
    you can set DB_ENGINE=sqlite to run against local SQLite.

Step 3: Run Migrations
    python manage.py makemigrations restaurant
    python manage.py migrate

Step 4: Initialize Role Groups and Superuser
    python manage.py setup_groups
    python manage.py createsuperuser


5. RUNNING THE APPLICATION
--------------------------------------------------------------------------------
Start the development server:
    python manage.py runserver

Open your browser:
    - Restaurant Homepage (Static HTML): http://127.0.0.1:8000/
    - Alternate static page endpoint:   http://127.0.0.1:8000/restaurant/
    - Django Admin portal:              http://127.0.0.1:8000/admin/
    - REST API Root:                    http://127.0.0.1:8000/api/


6. RUNNING AUTOMATED UNIT TESTS
--------------------------------------------------------------------------------
Run the full automated test suite:
    python manage.py test -v 2

Expected Result:
    37 tests run, 0 failures, 0 errors (OK).


7. AUTHENTICATION INSTRUCTIONS
--------------------------------------------------------------------------------
1. Register a new user:
   Endpoint: POST /api/users/
   Payload:  {"username": "customer1", "password": "Password123!", "email": "customer1@example.com"}
   Response: 201 Created

2. Obtain Auth Token:
   Endpoint: POST /api-token-auth/  (or POST /api/token/login/)
   Payload:  {"username": "customer1", "password": "Password123!"}
   Response: 200 OK -> {"token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b"}

3. Use Token on Protected Endpoints:
   Include the HTTP Header:
   Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b


8. COMPLETE API ENDPOINTS REFERENCE
--------------------------------------------------------------------------------

--------------------------------------------------------------------------------
A. STATIC HTML PAGE (Coursera Criterion 1)
--------------------------------------------------------------------------------
Method: GET
Path:   / or /restaurant/
Auth:   None (Public)
Status: 200 OK
Description: Renders the Little Lemon restaurant static HTML landing page with CSS.

--------------------------------------------------------------------------------
B. AUTHENTICATION & USER MANAGEMENT (Coursera Criterion 6)
--------------------------------------------------------------------------------
- Register user:
    POST /api/users/
    Auth: Public
    Body: {"username": "john", "password": "Password123", "email": "john@example.com"}
    Expected Status: 201 Created

- Obtain Token (Login):
    POST /api-token-auth/  (alias: /api/token/login/)
    Auth: Public
    Body: {"username": "john", "password": "Password123"}
    Expected Status: 200 OK

--------------------------------------------------------------------------------
C. CATEGORIES
--------------------------------------------------------------------------------
- List Categories:
    GET /api/categories/
    Auth: Public
    Expected Status: 200 OK

- Create Category:
    POST /api/categories/
    Auth: Admin only
    Body: {"title": "Appetizers", "slug": "appetizers"}
    Expected Status: 201 Created

--------------------------------------------------------------------------------
D. MENU ITEMS (Coursera Criterion 4)
--------------------------------------------------------------------------------
- List / Search / Filter / Order Menu Items:
    GET /api/menu-items/
    GET /api/menu-items/?search=Greek
    GET /api/menu-items/?category=1
    GET /api/menu-items/?category__slug=mains
    GET /api/menu-items/?ordering=-price
    GET /api/menu-items/?to_price=15.00
    Auth: Public
    Expected Status: 200 OK

- Retrieve Single Menu Item:
    GET /api/menu-items/{id}/
    Auth: Public
    Expected Status: 200 OK

- Create Menu Item:
    POST /api/menu-items/
    Auth: Manager or Admin
    Body: {"title": "Greek Salad", "price": "12.50", "category": 1, "featured": false}
    Expected Status: 201 Created (403 Forbidden for Customers)

- Update Menu Item:
    PUT/PATCH /api/menu-items/{id}/
    Auth: Manager or Admin
    Body: {"price": "13.00"}
    Expected Status: 200 OK

- Delete Menu Item:
    DELETE /api/menu-items/{id}/
    Auth: Manager or Admin
    Expected Status: 204 No Content

--------------------------------------------------------------------------------
E. TABLE BOOKING (Coursera Criterion 5)
--------------------------------------------------------------------------------
- List Bookings:
    GET /api/bookings/  (aliases: /api/booking/tables/ or /api/tables/)
    Auth: Authenticated
    Behavior: Customers see only their own bookings; Managers see all bookings.
    Expected Status: 200 OK (401 if unauthenticated)

- Create Booking:
    POST /api/bookings/
    Auth: Authenticated
    Body:
    {
      "name": "Mario Rossi",
      "no_of_guests": 4,
      "booking_date": "2026-12-25",
      "booking_time": "19:00:00",
      "table_number": 3,
      "special_requests": "Window table"
    }
    Expected Status: 201 Created

- Overlapping Conflict Validation:
    POST /api/bookings/
    Auth: Authenticated
    Body: (Same table_number, booking_date, and booking_time as an existing booking)
    Expected Status: 400 Bad Request
    Response: {"non_field_errors": ["Table 3 is already reserved for 2026-12-25 at 19:00:00."]}

- Retrieve / Update / Delete Booking:
    GET /api/bookings/{id}/
    PATCH /api/bookings/{id}/
    DELETE /api/bookings/{id}/
    Auth: Authenticated (Object-level authorization: customers can only access their own;
          managers can access all).
    Expected Status: 200 OK / 204 No Content (403/404 for unauthorized customer)

--------------------------------------------------------------------------------
F. CART & ORDERS
--------------------------------------------------------------------------------
- View Cart:
    GET /api/cart/menu-items/
    Auth: Authenticated Customer
    Expected Status: 200 OK

- Add to Cart:
    POST /api/cart/menu-items/
    Auth: Authenticated Customer
    Body: {"menuitem": 1, "quantity": 2}
    Expected Status: 201 Created

- Clear Cart:
    DELETE /api/cart/menu-items/
    Auth: Authenticated Customer
    Expected Status: 204 No Content

- Place Order from Cart:
    POST /api/orders/
    Auth: Authenticated Customer
    Expected Status: 201 Created

- List Orders:
    GET /api/orders/
    Auth: Authenticated (Customers see own orders; Delivery crew see assigned; Managers see all)
    Expected Status: 200 OK

- Update Order Status / Assign Delivery Crew:
    PATCH /api/orders/{id}/
    Auth: Manager (can set delivery_crew and status); Delivery Crew (can set status)
    Body: {"status": "delivered"} or {"delivery_crew": 2}
    Expected Status: 200 OK

--------------------------------------------------------------------------------
G. ROLE MANAGEMENT
--------------------------------------------------------------------------------
- Manager Group:
    GET/POST/DELETE /api/groups/manager/users/
    Auth: Admin only
    Body for POST/DELETE: {"username": "someuser"}

- Delivery Crew Group:
    GET/POST/DELETE /api/groups/delivery-crew/users/
    Auth: Manager or Admin
    Body for POST/DELETE: {"username": "someuser"}


9. INSOMNIA REST CLIENT TESTING INSTRUCTIONS
--------------------------------------------------------------------------------
1. Launch Insomnia.
2. Click "Create" -> "Import From" -> "File".
3. Select the file "Insomnia_LittleLemon_collection.json" in this repository root.
4. Set the environment variable:
   - "base_url": "http://127.0.0.1:8000"
   - "token": "<token obtained from request #2>"
5. Execute requests in sequence:
   - Request #1: User Registration
   - Request #2: Login / Obtain Token
   - Request #3: Static HTML Homepage
   - Request #4: List / Search Menu
   - Request #5: Create Menu Item
   - Request #6: List Table Bookings
   - Request #7: Create Table Reservation
   - Request #8: Overlap Conflict Test (Verifies 400 Bad Request error)
   - Request #9 - #12: Cart & Order Workflow


10. KNOWN LIMITATIONS & NOTES
--------------------------------------------------------------------------------
- If running in an environment without a running MySQL daemon, set DB_ENGINE=sqlite
  in your .env file to run locally on SQLite.
- Automated tests (manage.py test) automatically use an isolated in-memory test
  database so tests execute rapidly and reliably without external dependencies.
================================================================================
