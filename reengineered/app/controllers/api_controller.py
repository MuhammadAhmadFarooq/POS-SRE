"""
API Controller - RESTful API endpoints for the POS system.
Provides JSON API for potential frontend integration.
"""
from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from functools import wraps
from app.services.inventory_service import InventoryService
from app.services.transaction_service import TransactionService
from app.services.employee_service import EmployeeService
from app.services.rental_service import RentalService
from app.services.coupon_service import CouponService

api_bp = Blueprint('api', __name__)


def api_login_required(f):
    """Decorator for API authentication."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated_function


def api_admin_required(f):
    """Decorator for admin-only API endpoints."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return jsonify({'error': 'Authentication required'}), 401
        if not current_user.has_admin_access():
            return jsonify({'error': 'Admin access required'}), 403
        return f(*args, **kwargs)
    return decorated_function


# ============= ITEMS API =============

@api_bp.route('/items')
@api_login_required
def get_items():
    """Get all items."""
    item_type = request.args.get('type')
    items = InventoryService.get_all_items(item_type=item_type)
    return jsonify([item.to_dict() for item in items])


@api_bp.route('/items/<item_id>')
@api_login_required
def get_item(item_id):
    """Get item by ID."""
    item = InventoryService.get_item_by_id(item_id)
    if not item:
        return jsonify({'error': 'Item not found'}), 404
    return jsonify(item.to_dict())


@api_bp.route('/items/search')
@api_login_required
def search_items():
    """Search items."""
    query = request.args.get('q', '')
    item_type = request.args.get('type')
    
    if len(query) < 2:
        return jsonify([])
    
    items = InventoryService.search_items(query, item_type)
    return jsonify([item.to_dict() for item in items])


@api_bp.route('/items', methods=['POST'])
@api_admin_required
def create_item():
    """Create a new item."""
    data = request.get_json()
    
    try:
        item = InventoryService.add_item(
            item_id=data.get('item_id'),
            name=data.get('name'),
            price=data.get('price'),
            quantity=data.get('quantity', 0),
            item_type=data.get('item_type', 'sale'),
            description=data.get('description')
        )
        return jsonify(item.to_dict()), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@api_bp.route('/items/<item_id>', methods=['PUT'])
@api_admin_required
def update_item(item_id):
    """Update an item."""
    item = InventoryService.get_item_by_id(item_id)
    if not item:
        return jsonify({'error': 'Item not found'}), 404
    
    data = request.get_json()
    
    try:
        item = InventoryService.update_item(
            item,
            name=data.get('name'),
            price=data.get('price'),
            quantity=data.get('quantity'),
            description=data.get('description')
        )
        return jsonify(item.to_dict())
    except Exception as e:
        return jsonify({'error': str(e)}), 400


# ============= TRANSACTIONS API =============

@api_bp.route('/transactions')
@api_login_required
def get_transactions():
    """Get transactions."""
    limit = request.args.get('limit', 100, type=int)
    transaction_type = request.args.get('type')
    
    transactions = TransactionService.get_transactions(
        transaction_type=transaction_type,
        limit=limit
    )
    return jsonify([t.to_dict() for t in transactions])


@api_bp.route('/transactions/<transaction_number>')
@api_login_required
def get_transaction(transaction_number):
    """Get transaction by number."""
    transaction = TransactionService.get_transaction(transaction_number)
    if not transaction:
        return jsonify({'error': 'Transaction not found'}), 404
    return jsonify(transaction.to_dict())


@api_bp.route('/transactions', methods=['POST'])
@api_login_required
def create_transaction():
    """Create a new transaction (sale)."""
    data = request.get_json()
    
    try:
        transaction = TransactionService.create_sale(
            employee_id=current_user.id,
            items=data.get('items', []),
            payment_method=data.get('payment_method', 'cash'),
            amount_tendered=data.get('amount_tendered', 0),
            coupon_code=data.get('coupon_code'),
            customer_phone=data.get('customer_phone')
        )
        return jsonify(transaction.to_dict()), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400


# ============= EMPLOYEES API =============

@api_bp.route('/employees')
@api_admin_required
def get_employees():
    """Get all employees."""
    employees = EmployeeService.get_all_employees()
    return jsonify([e.to_dict() for e in employees])


@api_bp.route('/employees/<int:id>')
@api_admin_required
def get_employee(id):
    """Get employee by ID."""
    employee = EmployeeService.get_employee(id)
    if not employee:
        return jsonify({'error': 'Employee not found'}), 404
    return jsonify(employee.to_dict())


# ============= RENTALS API =============

@api_bp.route('/rentals')
@api_login_required
def get_rentals():
    """Get active rentals."""
    customer_phone = request.args.get('customer')
    rentals = RentalService.get_active_rentals(customer_phone)
    return jsonify([r.to_dict() for r in rentals])


@api_bp.route('/rentals/overdue')
@api_login_required
def get_overdue_rentals():
    """Get overdue rentals."""
    rentals = RentalService.get_overdue_rentals()
    return jsonify([r.to_dict() for r in rentals])


# ============= COUPONS API =============

@api_bp.route('/coupons/validate')
@api_login_required
def validate_coupon():
    """Validate a coupon code."""
    code = request.args.get('code', '')
    amount = request.args.get('amount', 0, type=float)
    
    result = CouponService.validate_coupon(code, amount)
    
    return jsonify({
        'valid': result['valid'],
        'message': result['message'],
        'discount': result.get('discount', 0)
    })


# ============= STATS API =============

@api_bp.route('/stats/dashboard')
@api_admin_required
def get_dashboard_stats():
    """Get dashboard statistics."""
    return jsonify({
        'employees': EmployeeService.get_employee_stats(),
        'inventory': InventoryService.get_inventory_stats(),
        'rentals': RentalService.get_rental_stats(),
        'daily_sales': TransactionService.get_daily_sales(),
        'coupons': CouponService.get_coupon_stats()
    })


@api_bp.route('/stats/daily-sales')
@api_admin_required
def get_daily_sales():
    """Get daily sales statistics."""
    from datetime import datetime
    date_str = request.args.get('date')
    
    if date_str:
        date = datetime.strptime(date_str, '%Y-%m-%d').date()
    else:
        date = None
    
    return jsonify(TransactionService.get_daily_sales(date))
