# Forward Engineering Documentation

## Phase 6: Forward Engineering

This document details the forward engineering phase - the construction of the new Python Flask-based POS system using the insights from reverse engineering and the refactored design.

---

## 1. Technology Selection

### 1.1 Technology Stack Decision Matrix

| Requirement | Options Considered | Selected | Rationale |
|-------------|-------------------|----------|-----------|
| Web Framework | Django, Flask, FastAPI | Flask | Lightweight, flexible, good for learning |
| Database | PostgreSQL, MySQL, SQLite | SQLite (dev) | Simple, no setup, portable |
| ORM | SQLAlchemy, Peewee | SQLAlchemy | Industry standard, Flask integration |
| Authentication | Custom, Flask-Login | Flask-Login | Proven, well-documented |
| Password Hashing | bcrypt, Werkzeug | Werkzeug | Included with Flask |
| Frontend | React, Vue, Bootstrap | Bootstrap 5 | No build step, responsive |
| Template Engine | Jinja2 (included) | Jinja2 | Native Flask support |

### 1.2 Dependencies

```txt
# requirements.txt
Flask>=2.3.0
Flask-SQLAlchemy>=3.0.0
Flask-Login>=0.6.0
Werkzeug>=2.3.0
python-dotenv>=1.0.0
```

---

## 2. Application Architecture

### 2.1 Directory Structure

```
reengineered/
├── app/
│   ├── __init__.py              # Flask app factory
│   ├── config.py                # Configuration classes
│   ├── models/                  # SQLAlchemy models
│   │   ├── __init__.py
│   │   ├── employee.py          # Employee model
│   │   ├── item.py              # Item model
│   │   ├── customer.py          # Customer model
│   │   ├── transaction.py       # Transaction models
│   │   ├── rental.py            # Rental model
│   │   └── coupon.py            # Coupon model
│   ├── services/                # Business logic layer
│   │   ├── __init__.py
│   │   ├── auth_service.py      # Authentication logic
│   │   ├── employee_service.py  # Employee management
│   │   ├── inventory_service.py # Stock management
│   │   ├── transaction_service.py # Transaction processing
│   │   ├── rental_service.py    # Rental lifecycle
│   │   └── coupon_service.py    # Coupon validation
│   ├── controllers/             # Flask blueprints (routes)
│   │   ├── __init__.py
│   │   ├── auth_controller.py   # /auth/* routes
│   │   ├── cashier_controller.py # /cashier/* routes
│   │   ├── admin_controller.py  # /admin/* routes
│   │   └── api_controller.py    # /api/* routes
│   ├── templates/               # Jinja2 templates
│   │   ├── base.html            # Base layout
│   │   ├── auth/
│   │   │   └── login.html
│   │   ├── cashier/
│   │   │   ├── dashboard.html
│   │   │   └── sale.html
│   │   ├── admin/
│   │   │   ├── dashboard.html
│   │   │   ├── employees/
│   │   │   │   └── list.html
│   │   │   └── inventory/
│   │   │       └── list.html
│   │   └── errors/
│   │       ├── 404.html
│   │       ├── 403.html
│   │       └── 500.html
│   └── static/                  # Static assets
│       ├── css/
│       ├── js/
│       └── images/
├── migrations/                  # Database migrations
│   └── migrate_data.py
├── tests/                       # Unit tests
├── run.py                       # Application entry point
└── requirements.txt             # Dependencies
```

### 2.2 Layer Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           PRESENTATION LAYER                            │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                    Templates (Jinja2 HTML)                       │   │
│  │  • base.html - Common layout, navigation, footer                 │   │
│  │  • auth/login.html - User authentication form                    │   │
│  │  • cashier/*.html - POS interface, sale processing               │   │
│  │  • admin/*.html - Dashboard, employee/inventory management       │   │
│  │  • errors/*.html - 404, 403, 500 error pages                     │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                 Controllers (Flask Blueprints)                   │   │
│  │  • auth_controller - Login/logout routes                         │   │
│  │  • cashier_controller - Cashier operations routes                │   │
│  │  • admin_controller - Admin panel routes                         │   │
│  │  • api_controller - RESTful JSON API routes                      │   │
│  └─────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         BUSINESS LOGIC LAYER                            │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                        Services                                  │   │
│  │  • AuthService - Authenticate, verify roles, manage sessions     │   │
│  │  • EmployeeService - CRUD operations, password management        │   │
│  │  • InventoryService - Stock tracking, low stock alerts           │   │
│  │  • TransactionService - Process sales, returns, calculate tax    │   │
│  │  • RentalService - Check out, check in, late fee calculation     │   │
│  │  • CouponService - Validate codes, apply discounts               │   │
│  └─────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                          DATA ACCESS LAYER                              │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                   Models (SQLAlchemy ORM)                        │   │
│  │  • Employee - id, username, password_hash, role, etc.            │   │
│  │  • Item - id, name, price, quantity, item_type, etc.             │   │
│  │  • Customer - id, phone, name, email, address                    │   │
│  │  • Transaction - id, type, total, items (relationship)           │   │
│  │  • TransactionItem - junction table for transaction items        │   │
│  │  • Rental - id, customer, item, due_date, returned, late_fee     │   │
│  │  • Coupon - id, code, discount_percent/amount, expires_at        │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                        Database                                  │   │
│  │  • SQLite (development) - pos_dev.db                             │   │
│  │  • PostgreSQL (production) - configurable via DATABASE_URL       │   │
│  └─────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Implementation Details

### 3.1 Application Factory Pattern

```python
# app/__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()

def create_app(config_name='development'):
    """Application factory pattern for flexible configuration."""
    app = Flask(__name__)
    
    # Load configuration
    from app.config import config
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    
    # Register blueprints
    from app.controllers.auth_controller import auth_bp
    from app.controllers.cashier_controller import cashier_bp
    from app.controllers.admin_controller import admin_bp
    from app.controllers.api_controller import api_bp
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(cashier_bp, url_prefix='/cashier')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # Register error handlers
    @app.errorhandler(404)
    def not_found(e):
        return render_template('errors/404.html'), 404
    
    return app
```

### 3.2 Configuration Classes

```python
# app/config.py
import os

class Config:
    """Base configuration."""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    TAX_RATE = 0.08  # 8% tax
    LATE_FEE_PER_DAY = 1.00

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///pos_dev.db'

class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')

class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
```

### 3.3 Model Implementation Example

```python
# app/models/employee.py
from app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class Employee(UserMixin, db.Model):
    """Employee model with authentication support."""
    __tablename__ = 'employees'
    
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.String(10), unique=True, nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    role = db.Column(db.String(20), default='Cashier')
    is_active = db.Column(db.Boolean, default=True)
    last_login = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    transactions = db.relationship('Transaction', backref='employee', lazy='dynamic')
    
    def set_password(self, password):
        """Hash and store password."""
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')
    
    def check_password(self, password):
        """Verify password against hash."""
        return check_password_hash(self.password_hash, password)
    
    @property
    def full_name(self):
        """Return full name."""
        return f"{self.first_name} {self.last_name}"
    
    def is_admin(self):
        """Check if employee has admin privileges."""
        return self.role in ['Admin', 'Manager']
    
    def to_dict(self):
        """Convert to dictionary for JSON API."""
        return {
            'id': self.id,
            'employee_id': self.employee_id,
            'username': self.username,
            'full_name': self.full_name,
            'role': self.role,
            'is_active': self.is_active,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }

@login_manager.user_loader
def load_user(user_id):
    """Load user by ID for Flask-Login."""
    return Employee.query.get(int(user_id))
```

### 3.4 Service Layer Example

```python
# app/services/transaction_service.py
from app import db
from app.models.transaction import Transaction, TransactionItem
from app.models.item import Item
from app.services.inventory_service import InventoryService
from app.services.coupon_service import CouponService
from datetime import datetime
from flask import current_app

class TransactionService:
    """Service for transaction processing."""
    
    @staticmethod
    def create_sale(employee_id, items_data, customer_id=None, coupon_code=None, 
                    payment_method='cash', amount_tendered=0):
        """
        Process a sale transaction.
        
        Args:
            employee_id: ID of cashier processing sale
            items_data: List of {'item_id': int, 'quantity': int}
            customer_id: Optional customer ID
            coupon_code: Optional discount coupon
            payment_method: 'cash', 'credit', 'debit', 'check'
            amount_tendered: Amount given by customer
            
        Returns:
            Transaction object if successful
            
        Raises:
            ValueError: If validation fails
        """
        # Validate items and calculate subtotal
        subtotal = 0
        transaction_items = []
        
        for item_data in items_data:
            item = Item.query.get(item_data['item_id'])
            if not item:
                raise ValueError(f"Item {item_data['item_id']} not found")
            if not item.is_active:
                raise ValueError(f"Item {item.name} is not available")
            if item.quantity < item_data['quantity']:
                raise ValueError(f"Insufficient stock for {item.name}")
            
            line_total = item.price * item_data['quantity']
            subtotal += line_total
            
            transaction_items.append({
                'item': item,
                'quantity': item_data['quantity'],
                'unit_price': item.price
            })
        
        # Apply coupon if provided
        discount_amount = 0
        coupon = None
        if coupon_code:
            coupon = CouponService.validate_coupon(coupon_code, subtotal)
            if coupon:
                discount_amount = CouponService.calculate_discount(coupon, subtotal)
        
        # Calculate tax and total
        tax_rate = current_app.config.get('TAX_RATE', 0.08)
        taxable_amount = subtotal - discount_amount
        tax_amount = round(taxable_amount * tax_rate, 2)
        total = round(taxable_amount + tax_amount, 2)
        
        # Validate payment
        if payment_method == 'cash':
            if amount_tendered < total:
                raise ValueError(f"Insufficient payment. Need ${total:.2f}")
            change_given = round(amount_tendered - total, 2)
        else:
            change_given = 0
        
        # Create transaction
        txn_number = TransactionService._generate_transaction_number()
        transaction = Transaction(
            transaction_number=txn_number,
            transaction_type='sale',
            employee_id=employee_id,
            customer_id=customer_id,
            coupon_id=coupon.id if coupon else None,
            subtotal=subtotal,
            discount_amount=discount_amount,
            tax_amount=tax_amount,
            total=total,
            payment_method=payment_method,
            amount_tendered=amount_tendered,
            change_given=change_given
        )
        
        db.session.add(transaction)
        db.session.flush()  # Get transaction ID
        
        # Add transaction items and update inventory
        for item_data in transaction_items:
            txn_item = TransactionItem(
                transaction_id=transaction.id,
                item_id=item_data['item'].id,
                quantity=item_data['quantity'],
                unit_price=item_data['unit_price']
            )
            db.session.add(txn_item)
            
            # Decrease inventory
            InventoryService.decrease_stock(
                item_data['item'].id, 
                item_data['quantity']
            )
        
        # Update coupon usage
        if coupon:
            CouponService.increment_usage(coupon.id)
        
        db.session.commit()
        return transaction
    
    @staticmethod
    def _generate_transaction_number():
        """Generate unique transaction number."""
        today = datetime.now().strftime('%Y%m%d')
        count = Transaction.query.filter(
            Transaction.transaction_number.like(f'TXN{today}%')
        ).count()
        return f"TXN{today}{count + 1:04d}"
```

### 3.5 Controller Example

```python
# app/controllers/api_controller.py
from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from app.services.inventory_service import InventoryService
from app.services.transaction_service import TransactionService
from functools import wraps

api_bp = Blueprint('api', __name__)

def admin_required(f):
    """Decorator to require admin role."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return jsonify({'error': 'Authentication required'}), 401
        if not current_user.is_admin():
            return jsonify({'error': 'Admin access required'}), 403
        return f(*args, **kwargs)
    return decorated_function

# Items API
@api_bp.route('/items', methods=['GET'])
@login_required
def get_items():
    """Get all items."""
    items = InventoryService.get_all_items()
    return jsonify({
        'success': True,
        'items': [item.to_dict() for item in items]
    })

@api_bp.route('/items/<int:item_id>', methods=['GET'])
@login_required
def get_item(item_id):
    """Get single item by ID."""
    item = InventoryService.get_item_by_id(item_id)
    if not item:
        return jsonify({'error': 'Item not found'}), 404
    return jsonify({
        'success': True,
        'item': item.to_dict()
    })

@api_bp.route('/items', methods=['POST'])
@admin_required
def create_item():
    """Create new item (admin only)."""
    data = request.get_json()
    try:
        item = InventoryService.add_item(
            item_id=data.get('item_id'),
            name=data['name'],
            price=data['price'],
            quantity=data.get('quantity', 0),
            item_type=data.get('item_type', 'sale'),
            description=data.get('description', '')
        )
        return jsonify({
            'success': True,
            'item': item.to_dict()
        }), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

# Transactions API
@api_bp.route('/transactions', methods=['POST'])
@login_required
def create_transaction():
    """Create a sale transaction."""
    data = request.get_json()
    try:
        transaction = TransactionService.create_sale(
            employee_id=current_user.id,
            items_data=data['items'],
            customer_id=data.get('customer_id'),
            coupon_code=data.get('coupon_code'),
            payment_method=data.get('payment_method', 'cash'),
            amount_tendered=data.get('amount_tendered', 0)
        )
        return jsonify({
            'success': True,
            'transaction': transaction.to_dict()
        }), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

# Dashboard Stats API
@api_bp.route('/stats/dashboard', methods=['GET'])
@login_required
def dashboard_stats():
    """Get dashboard statistics."""
    from app.models.transaction import Transaction
    from app.models.item import Item
    from app.models.rental import Rental
    from datetime import datetime, timedelta
    
    today = datetime.now().date()
    
    # Today's sales
    today_sales = Transaction.query.filter(
        Transaction.transaction_type == 'sale',
        db.func.date(Transaction.created_at) == today
    ).with_entities(
        db.func.sum(Transaction.total)
    ).scalar() or 0
    
    # Low stock items
    low_stock = Item.query.filter(
        Item.is_active == True,
        Item.quantity <= Item.low_stock_threshold
    ).count()
    
    # Overdue rentals
    overdue = Rental.query.filter(
        Rental.returned == False,
        Rental.due_date < datetime.now()
    ).count()
    
    return jsonify({
        'success': True,
        'stats': {
            'today_sales': round(today_sales, 2),
            'low_stock_count': low_stock,
            'overdue_rentals': overdue,
            'timestamp': datetime.now().isoformat()
        }
    })
```

---

## 4. User Interface

### 4.1 Template Inheritance

```html
<!-- templates/base.html -->
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}POS System{% endblock %}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.0/font/bootstrap-icons.css" rel="stylesheet">
    {% block extra_css %}{% endblock %}
</head>
<body class="d-flex flex-column min-vh-100">
    <!-- Navigation -->
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
        <!-- ... -->
    </nav>
    
    <!-- Flash Messages -->
    <div class="container mt-3">
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% for category, message in messages %}
                <div class="alert alert-{{ category }} alert-dismissible fade show">
                    {{ message }}
                    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                </div>
            {% endfor %}
        {% endwith %}
    </div>
    
    <!-- Main Content -->
    <main class="flex-grow-1">
        {% block content %}{% endblock %}
    </main>
    
    <!-- Footer -->
    <footer class="bg-light py-3 mt-auto">
        <div class="container text-center text-muted">
            &copy; 2024 POS System - Software Reengineering Project
        </div>
    </footer>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    {% block extra_js %}{% endblock %}
</body>
</html>
```

### 4.2 Responsive Design

The UI is built with Bootstrap 5 for responsive layouts:

- **Mobile-first** approach
- **Breakpoints**: xs, sm, md, lg, xl, xxl
- **Grid system** for flexible layouts
- **Components**: Cards, Tables, Forms, Modals

---

## 5. Security Implementation

### 5.1 Authentication Flow

```
┌─────────┐    ┌─────────────┐    ┌────────────┐    ┌──────────┐
│  User   │───►│ Login Form  │───►│ Validate   │───►│ Session  │
│         │    │             │    │ Credentials│    │ Created  │
└─────────┘    └─────────────┘    └────────────┘    └──────────┘
                                        │
                                        ▼
                               ┌────────────────┐
                               │ Hash Password  │
                               │ PBKDF2-SHA256  │
                               │ Compare Hash   │
                               └────────────────┘
```

### 5.2 Role-Based Access Control

```python
# Role hierarchy
ROLES = {
    'Admin': ['admin', 'cashier', 'reports', 'inventory', 'employees'],
    'Manager': ['cashier', 'reports', 'inventory'],
    'Cashier': ['cashier']
}

def role_required(role):
    """Decorator to check user role."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for('auth.login'))
            if role not in ROLES.get(current_user.role, []):
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator
```

---

## 6. API Documentation

### 6.1 RESTful Endpoints

| Method | Endpoint | Description | Auth | Role |
|--------|----------|-------------|------|------|
| POST | /auth/login | User login | No | - |
| GET | /auth/logout | User logout | Yes | All |
| GET | /api/items | List all items | Yes | All |
| GET | /api/items/:id | Get item details | Yes | All |
| POST | /api/items | Create item | Yes | Admin |
| PUT | /api/items/:id | Update item | Yes | Admin |
| DELETE | /api/items/:id | Delete item | Yes | Admin |
| GET | /api/transactions | List transactions | Yes | All |
| POST | /api/transactions | Create sale | Yes | All |
| GET | /api/employees | List employees | Yes | Admin |
| POST | /api/employees | Create employee | Yes | Admin |
| PUT | /api/employees/:id | Update employee | Yes | Admin |
| GET | /api/rentals | List rentals | Yes | All |
| GET | /api/rentals/overdue | List overdue | Yes | All |
| POST | /api/rentals | Create rental | Yes | All |
| PUT | /api/rentals/:id/return | Process return | Yes | All |
| GET | /api/coupons/validate | Validate coupon | Yes | All |
| GET | /api/stats/dashboard | Dashboard stats | Yes | All |

### 6.2 Request/Response Examples

**Create Sale:**
```json
// POST /api/transactions
// Request:
{
    "items": [
        {"item_id": 1, "quantity": 2},
        {"item_id": 5, "quantity": 1}
    ],
    "customer_id": 10,
    "coupon_code": "SAVE10",
    "payment_method": "cash",
    "amount_tendered": 50.00
}

// Response:
{
    "success": true,
    "transaction": {
        "id": 1234,
        "transaction_number": "TXN202401150001",
        "subtotal": 45.00,
        "discount_amount": 4.50,
        "tax_amount": 3.24,
        "total": 43.74,
        "change_given": 6.26,
        "created_at": "2024-01-15T10:30:00Z"
    }
}
```

---

## 7. Testing Strategy

### 7.1 Test Categories

| Category | Description | Coverage Target |
|----------|-------------|-----------------|
| Unit Tests | Individual functions/methods | 80% |
| Integration Tests | Service layer with database | 70% |
| API Tests | HTTP endpoint testing | 90% |
| UI Tests | Template rendering | 60% |

### 7.2 Test Example

```python
# tests/test_transaction_service.py
import pytest
from app import create_app, db
from app.models.employee import Employee
from app.models.item import Item
from app.services.transaction_service import TransactionService

class TestTransactionService:
    
    @pytest.fixture
    def app(self):
        app = create_app('testing')
        with app.app_context():
            db.create_all()
            yield app
            db.drop_all()
    
    @pytest.fixture
    def sample_employee(self, app):
        with app.app_context():
            emp = Employee(
                employee_id='E001',
                username='cashier1',
                first_name='Test',
                last_name='User',
                role='Cashier'
            )
            emp.set_password('password123')
            db.session.add(emp)
            db.session.commit()
            return emp
    
    @pytest.fixture
    def sample_item(self, app):
        with app.app_context():
            item = Item(
                item_id='I001',
                name='Test Item',
                price=9.99,
                quantity=100,
                item_type='sale'
            )
            db.session.add(item)
            db.session.commit()
            return item
    
    def test_create_sale_success(self, app, sample_employee, sample_item):
        with app.app_context():
            transaction = TransactionService.create_sale(
                employee_id=sample_employee.id,
                items_data=[{'item_id': sample_item.id, 'quantity': 2}],
                payment_method='cash',
                amount_tendered=30.00
            )
            
            assert transaction is not None
            assert transaction.transaction_type == 'sale'
            assert transaction.subtotal == 19.98
            assert transaction.items.count() == 1
    
    def test_create_sale_insufficient_stock(self, app, sample_employee, sample_item):
        with app.app_context():
            with pytest.raises(ValueError) as excinfo:
                TransactionService.create_sale(
                    employee_id=sample_employee.id,
                    items_data=[{'item_id': sample_item.id, 'quantity': 999}],
                    payment_method='cash',
                    amount_tendered=10000.00
                )
            assert 'Insufficient stock' in str(excinfo.value)
```

---

## 8. Deployment

### 8.1 Development

```bash
# Setup
python -m venv venv
.\venv\Scripts\activate  # Windows
pip install -r requirements.txt

# Initialize database
python -c "from app import create_app, db; app = create_app(); app.app_context().push(); db.create_all()"

# Run migration
python migrations/migrate_data.py

# Start development server
python run.py
```

### 8.2 Production Checklist

- [ ] Set `SECRET_KEY` environment variable
- [ ] Set `DATABASE_URL` for PostgreSQL
- [ ] Enable HTTPS
- [ ] Configure WSGI server (Gunicorn)
- [ ] Set up logging
- [ ] Configure backup strategy
- [ ] Enable rate limiting
- [ ] Set secure cookie flags

---

## 9. Summary

### Forward Engineering Achievements

| Component | Files Created | Purpose |
|-----------|--------------|---------|
| App Factory | 1 | Flexible initialization |
| Configuration | 1 | Environment-based config |
| Models | 6 | Database entities |
| Services | 6 | Business logic |
| Controllers | 4 | HTTP routing |
| Templates | 10+ | User interface |
| Migrations | 1 | Data migration |
| Entry Point | 1 | Application startup |

### Design Patterns Applied

| Pattern | Implementation |
|---------|---------------|
| Factory | `create_app()` function |
| Repository | SQLAlchemy models |
| Service Layer | `*Service` classes |
| MVC | Controllers, Models, Templates |
| Decorator | `@login_required`, `@admin_required` |
| Template Method | Transaction processing |

---

*Phase 6 completed as part of Software Reengineering project*
