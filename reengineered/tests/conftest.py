"""
Pytest configuration and fixtures for POS System tests.
"""
import pytest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.models import Employee, Item, Customer, Coupon


@pytest.fixture(scope='function')
def app():
    """Create application for testing."""
    # Create app with testing configuration
    app = create_app()
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'WTF_CSRF_ENABLED': False,
        'LOGIN_DISABLED': False,
    })
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture(scope='function')
def client(app):
    """Create test client."""
    return app.test_client()


@pytest.fixture(scope='function')
def runner(app):
    """Create CLI runner."""
    return app.test_cli_runner()


@pytest.fixture
def sample_employee(app):
    """Create a sample employee for testing."""
    with app.app_context():
        emp = Employee(
            employee_id='EMP001',
            username='testcashier',
            first_name='Test',
            last_name='Cashier',
            role='cashier'
        )
        emp.set_password('testpass123')
        db.session.add(emp)
        db.session.commit()
        return emp.id


@pytest.fixture
def sample_admin(app):
    """Create a sample admin for testing."""
    with app.app_context():
        admin = Employee(
            employee_id='ADM001',
            username='testadmin',
            first_name='Test',
            last_name='Admin',
            role='admin'
        )
        admin.set_password('adminpass123')
        db.session.add(admin)
        db.session.commit()
        return admin.id


@pytest.fixture
def sample_items(app):
    """Create sample items for testing."""
    with app.app_context():
        items = [
            Item(item_id='ITM001', name='Test Product 1', price=19.99, quantity=100, item_type='sale'),
            Item(item_id='ITM002', name='Test Product 2', price=29.99, quantity=50, item_type='sale'),
            Item(item_id='RNT001', name='Test Rental 1', price=9.99, quantity=10, item_type='rental'),
        ]
        for item in items:
            db.session.add(item)
        db.session.commit()
        return [item.id for item in items]


@pytest.fixture
def sample_customer(app):
    """Create a sample customer for testing."""
    with app.app_context():
        customer = Customer(
            phone='1234567890',
            name='Test Customer',
            email='test@example.com'
        )
        db.session.add(customer)
        db.session.commit()
        return customer.id


@pytest.fixture
def sample_coupon(app):
    """Create a sample coupon for testing."""
    with app.app_context():
        coupon = Coupon(
            code='TEST10',
            discount_type='percentage',
            discount_value=10.0,
            is_active=True
        )
        db.session.add(coupon)
        db.session.commit()
        return coupon.id
