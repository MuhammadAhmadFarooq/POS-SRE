"""
Unit tests for SQLAlchemy models.
Tests model creation, validation, and methods.
"""
import pytest
from app.models import Employee, Item, Transaction, Customer, Rental, Coupon
from app import db


class TestEmployeeModel:
    """Tests for Employee model."""
    
    def test_password_hashing(self, app):
        """Test that passwords are properly hashed."""
        with app.app_context():
            emp = Employee(
                username='hashtest',
                first_name='Hash',
                last_name='Test',
                role='cashier'
            )
            emp.set_password('secret123')
            
            # Password should be hashed, not plain text
            assert emp.password_hash != 'secret123'
            assert emp.password_hash is not None
            
            # Check password should work correctly
            assert emp.check_password('secret123') is True
            assert emp.check_password('wrongpassword') is False
    
    def test_employee_creation(self, app):
        """Test employee creation and retrieval."""
        with app.app_context():
            emp = Employee(
                employee_id='EMP999',
                username='newemployee',
                first_name='New',
                last_name='Employee',
                role='manager'
            )
            emp.set_password('password123')
            db.session.add(emp)
            db.session.commit()
            
            # Retrieve and verify
            retrieved = Employee.query.filter_by(username='newemployee').first()
            assert retrieved is not None
            assert retrieved.first_name == 'New'
            assert retrieved.last_name == 'Employee'
            assert retrieved.role == 'manager'
            assert retrieved.is_active is True
    
    def test_employee_full_name(self, app):
        """Test full name property."""
        with app.app_context():
            emp = Employee(
                username='fullnametest',
                first_name='John',
                last_name='Doe',
                role='cashier'
            )
            assert emp.full_name == 'John Doe'
    
    def test_employee_roles(self, app):
        """Test different employee roles."""
        with app.app_context():
            roles = ['admin', 'manager', 'cashier']
            for i, role in enumerate(roles):
                emp = Employee(
                    employee_id=f'ROLE{i}',
                    username=f'user_{role}',
                    first_name='Test',
                    last_name=role.capitalize(),
                    role=role
                )
                emp.set_password('pass')
                db.session.add(emp)
            db.session.commit()
            
            for role in roles:
                emp = Employee.query.filter_by(role=role).first()
                assert emp is not None


class TestItemModel:
    """Tests for Item model."""
    
    def test_item_creation(self, app):
        """Test item creation."""
        with app.app_context():
            item = Item(
                item_id='ITEM001',
                name='Test Product',
                price=29.99,
                quantity=100,
                item_type='sale'
            )
            db.session.add(item)
            db.session.commit()
            
            assert item.id is not None
            assert item.is_active is True
            assert item.low_stock_threshold == 10  # Default
    
    def test_item_to_dict(self, app):
        """Test item serialization."""
        with app.app_context():
            item = Item(
                item_id='DICT001',
                name='Widget',
                price=19.99,
                quantity=50,
                item_type='sale',
                description='A test widget'
            )
            db.session.add(item)
            db.session.commit()
            
            item_dict = item.to_dict()
            assert item_dict['name'] == 'Widget'
            assert item_dict['price'] == 19.99
            assert item_dict['quantity'] == 50
            assert 'id' in item_dict
    
    def test_item_types(self, app):
        """Test sale and rental item types."""
        with app.app_context():
            sale_item = Item(item_id='SALE01', name='Sale Item', 
                           price=10.00, quantity=20, item_type='sale')
            rental_item = Item(item_id='RENT01', name='Rental Item',
                             price=5.00, quantity=10, item_type='rental')
            
            db.session.add_all([sale_item, rental_item])
            db.session.commit()
            
            sales = Item.query.filter_by(item_type='sale').all()
            rentals = Item.query.filter_by(item_type='rental').all()
            
            assert len(sales) >= 1
            assert len(rentals) >= 1


class TestCustomerModel:
    """Tests for Customer model."""
    
    def test_customer_creation(self, app):
        """Test customer creation."""
        with app.app_context():
            customer = Customer(
                phone='5551234567',
                name='Jane Doe',
                email='jane@example.com',
                address='123 Main St'
            )
            db.session.add(customer)
            db.session.commit()
            
            assert customer.id is not None
            assert customer.is_active is True
    
    def test_customer_phone_lookup(self, app):
        """Test customer lookup by phone."""
        with app.app_context():
            customer = Customer(
                phone='5559876543',
                name='Phone Test'
            )
            db.session.add(customer)
            db.session.commit()
            
            found = Customer.query.filter_by(phone='5559876543').first()
            assert found is not None
            assert found.name == 'Phone Test'


class TestCouponModel:
    """Tests for Coupon model."""
    
    def test_percentage_coupon(self, app):
        """Test percentage discount coupon."""
        with app.app_context():
            coupon = Coupon(
                code='PERCENT20',
                discount_type='percentage',
                discount_value=20.0,
                is_active=True
            )
            db.session.add(coupon)
            db.session.commit()
            
            found = Coupon.query.filter_by(code='PERCENT20').first()
            assert found is not None
            assert found.discount_type == 'percentage'
            assert found.discount_value == 20.0
    
    def test_fixed_coupon(self, app):
        """Test fixed amount discount coupon."""
        with app.app_context():
            coupon = Coupon(
                code='FIXED5',
                discount_type='fixed',
                discount_value=5.0,
                is_active=True
            )
            db.session.add(coupon)
            db.session.commit()
            
            found = Coupon.query.filter_by(code='FIXED5').first()
            assert found is not None
            assert found.discount_type == 'fixed'
    
    def test_inactive_coupon(self, app):
        """Test inactive coupon filtering."""
        with app.app_context():
            coupon = Coupon(
                code='INACTIVE',
                discount_type='percentage',
                discount_value=50.0,
                is_active=False
            )
            db.session.add(coupon)
            db.session.commit()
            
            active_coupons = Coupon.query.filter_by(is_active=True).all()
            inactive = Coupon.query.filter_by(code='INACTIVE').first()
            
            assert inactive not in active_coupons
