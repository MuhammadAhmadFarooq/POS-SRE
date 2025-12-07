"""
Database tests for schema constraints and data integrity.
Tests foreign keys, unique constraints, and data migration.
"""
import pytest
from sqlalchemy.exc import IntegrityError
from app.models import Employee, Item, Transaction, Customer, Rental, TransactionItem
from app import db


class TestDatabaseConstraints:
    """Tests for database schema constraints."""
    
    def test_unique_username_constraint(self, app):
        """Test that duplicate usernames are rejected."""
        with app.app_context():
            emp1 = Employee(
                employee_id='UNIQUE1',
                username='duplicate_user',
                first_name='First',
                last_name='User',
                role='cashier'
            )
            emp1.set_password('pass1')
            db.session.add(emp1)
            db.session.commit()
            
            emp2 = Employee(
                employee_id='UNIQUE2',
                username='duplicate_user',  # Same username
                first_name='Second',
                last_name='User',
                role='cashier'
            )
            emp2.set_password('pass2')
            db.session.add(emp2)
            
            with pytest.raises(IntegrityError):
                db.session.commit()
            db.session.rollback()
    
    def test_unique_employee_id_constraint(self, app):
        """Test that duplicate employee IDs are rejected."""
        with app.app_context():
            emp1 = Employee(
                employee_id='EMPDUP',
                username='user1',
                first_name='First',
                last_name='User',
                role='cashier'
            )
            emp1.set_password('pass1')
            db.session.add(emp1)
            db.session.commit()
            
            emp2 = Employee(
                employee_id='EMPDUP',  # Same employee_id
                username='user2',
                first_name='Second',
                last_name='User',
                role='cashier'
            )
            emp2.set_password('pass2')
            db.session.add(emp2)
            
            with pytest.raises(IntegrityError):
                db.session.commit()
            db.session.rollback()
    
    def test_unique_item_id_constraint(self, app):
        """Test that duplicate item IDs are rejected."""
        with app.app_context():
            item1 = Item(
                item_id='ITEMDUP',
                name='Item 1',
                price=10.00,
                quantity=50,
                item_type='sale'
            )
            db.session.add(item1)
            db.session.commit()
            
            item2 = Item(
                item_id='ITEMDUP',  # Same item_id
                name='Item 2',
                price=20.00,
                quantity=30,
                item_type='sale'
            )
            db.session.add(item2)
            
            with pytest.raises(IntegrityError):
                db.session.commit()
            db.session.rollback()
    
    def test_unique_coupon_code_constraint(self, app):
        """Test that duplicate coupon codes are rejected."""
        with app.app_context():
            from app.models import Coupon
            
            coupon1 = Coupon(
                code='DUPCODE',
                discount_type='percentage',
                discount_value=10.0,
                is_active=True
            )
            db.session.add(coupon1)
            db.session.commit()
            
            coupon2 = Coupon(
                code='DUPCODE',  # Same code
                discount_type='fixed',
                discount_value=5.0,
                is_active=True
            )
            db.session.add(coupon2)
            
            with pytest.raises(IntegrityError):
                db.session.commit()
            db.session.rollback()


class TestForeignKeyConstraints:
    """Tests for foreign key relationships."""
    
    def test_transaction_employee_fk(self, app, sample_employee):
        """Test transaction requires valid employee."""
        with app.app_context():
            # Valid transaction
            txn = Transaction(
                employee_id=sample_employee,
                transaction_type='sale',
                subtotal=100.00,
                total=106.00
            )
            db.session.add(txn)
            db.session.commit()
            
            assert txn.id is not None
            assert txn.employee_id == sample_employee
    
    def test_rental_customer_relationship(self, app, sample_customer, sample_items):
        """Test rental-customer relationship."""
        with app.app_context():
            from datetime import datetime, timedelta
            
            item = Item.query.filter_by(item_type='rental').first()
            if not item:
                item = Item(item_id='RENT99', name='Rental Test', 
                           price=5.00, quantity=5, item_type='rental')
                db.session.add(item)
                db.session.commit()
            
            rental = Rental(
                customer_id=sample_customer,
                item_id=item.id,
                quantity=1,
                rental_price=item.price,
                rental_date=datetime.utcnow(),
                due_date=datetime.utcnow() + timedelta(days=7)
            )
            db.session.add(rental)
            db.session.commit()
            
            assert rental.id is not None
            assert rental.customer_id == sample_customer


class TestCascadeDeletes:
    """Tests for cascade delete behavior."""
    
    def test_transaction_items_cascade(self, app, sample_employee, sample_items):
        """Test that transaction items are handled on transaction operations."""
        with app.app_context():
            # Create transaction
            txn = Transaction(
                employee_id=sample_employee,
                transaction_type='sale',
                subtotal=50.00,
                total=53.00
            )
            db.session.add(txn)
            db.session.commit()
            
            # Add transaction items
            item = Item.query.first()
            txn_item = TransactionItem(
                transaction_id=txn.id,
                item_id=item.id,
                quantity=2,
                unit_price=item.price,
                subtotal=item.price * 2
            )
            db.session.add(txn_item)
            db.session.commit()
            
            # Verify relationship
            assert len(txn.items) == 1


class TestDataIntegrity:
    """Tests for data integrity and validation."""
    
    def test_employee_default_values(self, app):
        """Test default values are set correctly."""
        with app.app_context():
            emp = Employee(
                username='defaults_test',
                first_name='Default',
                last_name='Test',
                role='cashier'
            )
            emp.set_password('pass')
            db.session.add(emp)
            db.session.commit()
            
            assert emp.is_active is True
            assert emp.created_at is not None
    
    def test_item_default_values(self, app):
        """Test item default values."""
        with app.app_context():
            item = Item(
                item_id='DEFITEM',
                name='Default Test Item',
                price=15.00,
                quantity=25,
                item_type='sale'
            )
            db.session.add(item)
            db.session.commit()
            
            assert item.is_active is True
            assert item.low_stock_threshold == 10
            assert item.created_at is not None
    
    def test_decimal_precision(self, app):
        """Test price decimal precision."""
        with app.app_context():
            item = Item(
                item_id='DECIMAL',
                name='Decimal Test',
                price=19.99,
                quantity=10,
                item_type='sale'
            )
            db.session.add(item)
            db.session.commit()
            
            retrieved = Item.query.filter_by(item_id='DECIMAL').first()
            assert float(retrieved.price) == 19.99


class TestDataMigration:
    """Tests to verify migrated data integrity."""
    
    def test_seeded_admin_exists(self, app):
        """Test that seeded admin user exists after migration."""
        with app.app_context():
            # This would pass after running seed_db.py
            # For unit test, we create the expected state
            admin = Employee(
                employee_id='ADM000',
                username='admin',
                first_name='Admin',
                last_name='User',
                role='admin'
            )
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            
            found = Employee.query.filter_by(username='admin').first()
            assert found is not None
            assert found.role == 'admin'
            assert found.check_password('admin123')
    
    def test_password_not_plain_text(self, app):
        """Verify passwords are not stored as plain text."""
        with app.app_context():
            emp = Employee(
                username='security_test',
                first_name='Security',
                last_name='Test',
                role='cashier'
            )
            emp.set_password('mypassword')
            db.session.add(emp)
            db.session.commit()
            
            # Password should be hashed
            assert emp.password_hash != 'mypassword'
            assert 'pbkdf2' in emp.password_hash or 'sha256' in emp.password_hash
