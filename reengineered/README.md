# Reengineered Point-of-Sale (POS) System

## Project Overview

This is a modern, web-based Point-of-Sale system reengineered from a legacy Java Swing desktop application. The system has been completely transformed using the **Software Reengineering Process Model** with the following phases:

1. **Inventory Analysis** - Identified and classified all software assets
2. **Document Restructuring** - Rebuilt technical documentation
3. **Reverse Engineering** - Recovered design, data structures, and logic
4. **Code Restructuring** - Improved maintainability and readability
5. **Data Restructuring** - Migrated from .txt files to SQLite database
6. **Forward Engineering** - Developed modern web-based application

## Technology Stack

### Backend
- **Language**: Python 3.10+
- **Framework**: Flask 2.3+
- **ORM**: SQLAlchemy
- **Database**: SQLite (development) / PostgreSQL (production)
- **Authentication**: Flask-Login with password hashing (Werkzeug)

### Frontend
- **Template Engine**: Jinja2
- **CSS Framework**: Bootstrap 5
- **JavaScript**: Vanilla JS with Fetch API

### Architecture
- **Pattern**: Model-View-Controller (MVC)
- **Layers**: 
  - Presentation Layer (Templates/Views)
  - Business Logic Layer (Services)
  - Data Access Layer (Models/Repository)

## Project Structure

```
reengineered/
├── app/
│   ├── __init__.py              # Flask app factory
│   ├── config.py                # Configuration settings
│   ├── models/                  # Data models (SQLAlchemy)
│   │   ├── __init__.py
│   │   ├── user.py              # User/Employee model
│   │   ├── item.py              # Item/Product model
│   │   ├── customer.py          # Customer model
│   │   ├── transaction.py       # Transaction model
│   │   ├── rental.py            # Rental model
│   │   └── coupon.py            # Coupon model
│   ├── services/                # Business logic layer
│   │   ├── __init__.py
│   │   ├── auth_service.py      # Authentication service
│   │   ├── inventory_service.py # Inventory management
│   │   ├── transaction_service.py # Transaction processing
│   │   ├── rental_service.py    # Rental management
│   │   └── employee_service.py  # Employee management
│   ├── controllers/             # Route handlers
│   │   ├── __init__.py
│   │   ├── auth_controller.py   # Login/Logout routes
│   │   ├── cashier_controller.py # Cashier operations
│   │   ├── admin_controller.py  # Admin operations
│   │   └── api_controller.py    # REST API endpoints
│   ├── templates/               # Jinja2 templates
│   │   ├── base.html
│   │   ├── auth/
│   │   ├── cashier/
│   │   └── admin/
│   └── static/                  # CSS, JS, images
│       ├── css/
│       └── js/
├── migrations/                  # Database migrations
│   └── migrate_data.py          # Data migration script
├── tests/                       # Unit tests
├── docs/                        # Documentation
│   ├── INVENTORY_ANALYSIS.md
│   ├── REVERSE_ENGINEERING.md
│   ├── REFACTORING_LOG.md
│   └── ARCHITECTURE.md
├── requirements.txt             # Python dependencies
├── run.py                       # Application entry point
└── README.md                    # This file
```

## Installation & Setup

### Prerequisites
- Python 3.10 or higher
- pip (Python package manager)

### Installation Steps

1. **Navigate to the reengineered directory**:
   ```bash
   cd reengineered
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment**:
   - Windows: `venv\Scripts\activate`
   - Linux/Mac: `source venv/bin/activate`

4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

5. **Initialize the database**:
   ```bash
   python -c "from app import create_app, db; app = create_app(); app.app_context().push(); db.create_all()"
   ```

6. **Migrate data from legacy system** (optional):
   ```bash
   python migrations/migrate_data.py
   ```

7. **Run the application**:
   ```bash
   python run.py
   ```

8. **Access the application**:
   Open a web browser and navigate to `http://localhost:5000`

## Default Login Credentials

After migration, use the following credentials:
- **Admin**: Username: `110001`, Password: `1`
- **Cashier**: Username: `110002`, Password: `lehigh2016`

## Features

### Authentication
- Secure login with password hashing
- Role-based access control (Admin/Cashier)
- Session management with logout functionality

### Cashier Operations
- Process sales transactions
- Handle item rentals
- Process returns (rented items and unsatisfactory items)
- Apply coupon discounts
- Cash and electronic payment processing

### Admin Operations
- View all employees
- Add new employees (Cashier/Admin)
- Update employee information
- Remove employees
- Switch to Cashier view

### Inventory Management
- View inventory levels
- Track stock quantities
- Automatic inventory updates on transactions

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/items` | GET | List all items |
| `/api/items/<id>` | GET | Get item details |
| `/api/cart/add` | POST | Add item to cart |
| `/api/cart/remove` | POST | Remove item from cart |
| `/api/transaction/complete` | POST | Complete transaction |
| `/api/employees` | GET | List employees (Admin) |
| `/api/employees` | POST | Add employee (Admin) |

## Comparison: Legacy vs Reengineered

| Aspect | Legacy System | Reengineered System |
|--------|---------------|---------------------|
| Architecture | Monolithic desktop | Layered web MVC |
| UI Technology | Java Swing | HTML/CSS/Bootstrap |
| Data Storage | Plain text files | SQLite/PostgreSQL |
| Authentication | Plain text passwords | Hashed passwords |
| Accessibility | Single machine | Any device with browser |
| Maintainability | Poor (tightly coupled) | Good (separation of concerns) |
| Testability | Difficult | Easy (unit tests) |
| Scalability | Limited | Horizontally scalable |

## License

This project is developed for educational purposes as part of a Software Reengineering course.

## Contributors

- Student Team (SRE Project - Semester 7)
