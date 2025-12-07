"""
Integration tests for service layer.
Tests business logic with database interactions.
"""
import pytest
from app.models import Employee, Item, Customer, Transaction, Coupon
from app.services import AuthService, InventoryService, TransactionService, CouponService
from app import db


class TestAuthService:
    """Tests for authentication service."""
    
    def test_authenticate_valid_user(self, app, sample_employee):
        """Test successful authentication."""
        with app.app_context():
            result = AuthService.authenticate('testcashier', 'testpass123')
            assert result is not None
            assert result.username == 'testcashier'
    
    def test_authenticate_invalid_password(self, app, sample_employee):
        """Test authentication with wrong password."""
        with app.app_context():
            result = AuthService.authenticate('testcashier', 'wrongpassword')
            assert result is None
    
    def test_authenticate_nonexistent_user(self, app):
        """Test authentication with non-existent user."""
        with app.app_context():
            result = AuthService.authenticate('nobody', 'anypassword')
            assert result is None
    
    def test_authenticate_inactive_user(self, app):
        """Test authentication with inactive user."""
        with app.app_context():
            emp = Employee(
                username='inactive_user',
                first_name='Inactive',
                last_name='User',
                role='cashier',
                is_active=False
            )
            emp.set_password('password')
            db.session.add(emp)
            db.session.commit()
            
            result = AuthService.authenticate('inactive_user', 'password')
            assert result is None


class TestInventoryService:
    """Tests for inventory service."""
    
    def test_get_all_items(self, app, sample_items):
        """Test retrieving all items."""
        with app.app_context():
            items = InventoryService.get_all_items()
            assert len(items) >= 3
    
    def test_get_sale_items(self, app, sample_items):
        """Test retrieving sale items only."""
        with app.app_context():
            sale_items = InventoryService.get_items_by_type('sale')
            for item in sale_items:
                assert item.item_type == 'sale'
    
    def test_get_rental_items(self, app, sample_items):
        """Test retrieving rental items only."""
        with app.app_context():
            rental_items = InventoryService.get_items_by_type('rental')
            for item in rental_items:
                assert item.item_type == 'rental'
    
    def test_update_stock_decrease(self, app, sample_items):
        """Test decreasing stock."""
        with app.app_context():
            item = Item.query.filter_by(item_id='ITM001').first()
            original_qty = item.quantity
            
            InventoryService.update_stock(item.id, -5)
            
            updated = Item.query.get(item.id)
            assert updated.quantity == original_qty - 5
    
    def test_update_stock_increase(self, app, sample_items):
        """Test increasing stock."""
        with app.app_context():
            item = Item.query.filter_by(item_id='ITM001').first()
            original_qty = item.quantity
            
            InventoryService.update_stock(item.id, 10)
            
            updated = Item.query.get(item.id)
            assert updated.quantity == original_qty + 10
    
    def test_get_low_stock_items(self, app):
        """Test low stock detection."""
        with app.app_context():
            # Create item with low stock
            low_item = Item(
                item_id='LOW001',
                name='Low Stock Item',
                price=5.00,
                quantity=3,
                item_type='sale',
                low_stock_threshold=10
            )
            db.session.add(low_item)
            db.session.commit()
            
            low_stock = InventoryService.get_low_stock_items()
            item_ids = [i.item_id for i in low_stock]
            assert 'LOW001' in item_ids
    
    def test_search_items(self, app, sample_items):
        """Test item search functionality."""
        with app.app_context():
            results = InventoryService.search_items('Test Product')
            assert len(results) >= 1


class TestCouponService:
    """Tests for coupon service."""
    
    def test_validate_active_coupon(self, app, sample_coupon):
        """Test validating an active coupon."""
        with app.app_context():
            coupon = CouponService.validate_coupon('TEST10')
            assert coupon is not None
            assert coupon.code == 'TEST10'
    
    def test_validate_invalid_coupon(self, app):
        """Test validating non-existent coupon."""
        with app.app_context():
            coupon = CouponService.validate_coupon('INVALID')
            assert coupon is None
    
    def test_calculate_percentage_discount(self, app, sample_coupon):
        """Test percentage discount calculation."""
        with app.app_context():
            coupon = Coupon.query.filter_by(code='TEST10').first()
            subtotal = 100.00
            discount = CouponService.calculate_discount(coupon, subtotal)
            assert discount == 10.00  # 10% of 100
    
    def test_calculate_fixed_discount(self, app):
        """Test fixed discount calculation."""
        with app.app_context():
            coupon = Coupon(
                code='FIXED10',
                discount_type='fixed',
                discount_value=10.0,
                is_active=True
            )
            db.session.add(coupon)
            db.session.commit()
            
            subtotal = 50.00
            discount = CouponService.calculate_discount(coupon, subtotal)
            assert discount == 10.00


class TestTransactionService:
    """Tests for transaction service."""
    
    def test_create_sale_transaction(self, app, sample_employee, sample_items):
        """Test creating a sale transaction."""
        with app.app_context():
            emp = Employee.query.get(sample_employee)
            items = Item.query.filter_by(item_type='sale').limit(2).all()
            
            cart = [
                {'item_id': items[0].id, 'quantity': 2, 'price': items[0].price},
                {'item_id': items[1].id, 'quantity': 1, 'price': items[1].price}
            ]
            
            transaction = TransactionService.create_sale(
                employee_id=emp.id,
                cart_items=cart
            )
            
            assert transaction is not None
            assert transaction.transaction_type == 'sale'
            assert transaction.total > 0
    
    def test_transaction_updates_inventory(self, app, sample_employee, sample_items):
        """Test that sale updates inventory."""
        with app.app_context():
            item = Item.query.filter_by(item_id='ITM001').first()
            original_qty = item.quantity
            
            cart = [{'item_id': item.id, 'quantity': 3, 'price': item.price}]
            
            TransactionService.create_sale(
                employee_id=sample_employee,
                cart_items=cart
            )
            
            updated_item = Item.query.get(item.id)
            assert updated_item.quantity == original_qty - 3
