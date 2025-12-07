"""
Cashier Controller - Handles cashier operations.
Replaces legacy Cashier_Interface.java, Transaction_Interface.java, etc.
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from functools import wraps
from app.services.inventory_service import InventoryService
from app.services.transaction_service import TransactionService, TransactionError
from app.services.rental_service import RentalService
from app.services.coupon_service import CouponService
from app.models.item import ItemType
from app.models.transaction import PaymentMethod

cashier_bp = Blueprint('cashier', __name__)


def cashier_required(f):
    """Decorator to require cashier or higher role."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login'))
        # All authenticated users can access cashier functions
        return f(*args, **kwargs)
    return decorated_function


@cashier_bp.route('/dashboard')
@login_required
@cashier_required
def dashboard():
    """Cashier dashboard."""
    stats = TransactionService.get_daily_sales()
    return render_template('cashier/dashboard.html', stats=stats)


@cashier_bp.route('/sale', methods=['GET', 'POST'])
@login_required
@cashier_required
def new_sale():
    """Create a new sale transaction."""
    if request.method == 'POST':
        try:
            # Get form data
            items_json = request.form.get('items', '[]')
            import json
            items = json.loads(items_json)
            
            if not items:
                flash('No items in cart', 'warning')
                return redirect(url_for('cashier.new_sale'))
            
            payment_method = request.form.get('payment_method', PaymentMethod.CASH)
            amount_tendered = float(request.form.get('amount_tendered', 0))
            coupon_code = request.form.get('coupon_code', '').strip() or None
            customer_phone = request.form.get('customer_phone', '').strip() or None
            
            # Process sale
            transaction = TransactionService.create_sale(
                employee_id=current_user.id,
                items=items,
                payment_method=payment_method,
                amount_tendered=amount_tendered,
                coupon_code=coupon_code,
                customer_phone=customer_phone
            )
            
            flash(f'Sale completed! Transaction: {transaction.transaction_number}', 'success')
            return redirect(url_for('cashier.receipt', transaction_number=transaction.transaction_number))
            
        except TransactionError as e:
            flash(str(e), 'danger')
        except Exception as e:
            flash(f'Error processing sale: {str(e)}', 'danger')
    
    # Get sale items for display
    items = InventoryService.get_sale_items()
    return render_template('cashier/sale.html', items=items, payment_methods=PaymentMethod.all_methods())


@cashier_bp.route('/rental', methods=['GET', 'POST'])
@login_required
@cashier_required
def new_rental():
    """Create a new rental transaction."""
    if request.method == 'POST':
        try:
            # Get form data
            items_json = request.form.get('items', '[]')
            import json
            items = json.loads(items_json)
            
            if not items:
                flash('No items in cart', 'warning')
                return redirect(url_for('cashier.new_rental'))
            
            customer_phone = request.form.get('customer_phone', '').strip()
            if not customer_phone:
                flash('Customer phone is required for rentals', 'warning')
                return redirect(url_for('cashier.new_rental'))
            
            rental_days = int(request.form.get('rental_days', 7))
            payment_method = request.form.get('payment_method', PaymentMethod.CASH)
            amount_tendered = float(request.form.get('amount_tendered', 0))
            
            # Process rental
            transaction = TransactionService.create_rental(
                employee_id=current_user.id,
                customer_phone=customer_phone,
                items=items,
                rental_days=rental_days,
                payment_method=payment_method,
                amount_tendered=amount_tendered
            )
            
            flash(f'Rental completed! Transaction: {transaction.transaction_number}', 'success')
            return redirect(url_for('cashier.receipt', transaction_number=transaction.transaction_number))
            
        except TransactionError as e:
            flash(str(e), 'danger')
        except Exception as e:
            flash(f'Error processing rental: {str(e)}', 'danger')
    
    # Get rental items for display
    items = InventoryService.get_rental_items()
    return render_template('cashier/rental.html', items=items, payment_methods=PaymentMethod.all_methods())


@cashier_bp.route('/return', methods=['GET', 'POST'])
@login_required
@cashier_required
def process_return():
    """Process a rental return."""
    if request.method == 'POST':
        try:
            customer_phone = request.form.get('customer_phone', '').strip()
            item_id = request.form.get('item_id', '').strip()
            
            if not customer_phone or not item_id:
                flash('Customer phone and item ID are required', 'warning')
                return redirect(url_for('cashier.process_return'))
            
            # Process return
            result = TransactionService.process_return(
                employee_id=current_user.id,
                customer_phone=customer_phone,
                item_id=item_id
            )
            
            if result['late_fee'] > 0:
                flash(f"Return processed. Late fee: ${result['late_fee']:.2f}", 'warning')
            else:
                flash('Return processed successfully!', 'success')
            
            return redirect(url_for('cashier.dashboard'))
            
        except TransactionError as e:
            flash(str(e), 'danger')
        except Exception as e:
            flash(f'Error processing return: {str(e)}', 'danger')
    
    # Get overdue rentals for display
    overdue = RentalService.get_overdue_rentals()
    active = RentalService.get_active_rentals()
    return render_template('cashier/return.html', overdue=overdue, active=active)


@cashier_bp.route('/receipt/<transaction_number>')
@login_required
@cashier_required
def receipt(transaction_number):
    """Display transaction receipt."""
    transaction = TransactionService.get_transaction(transaction_number)
    if not transaction:
        flash('Transaction not found', 'danger')
        return redirect(url_for('cashier.dashboard'))
    
    return render_template('cashier/receipt.html', transaction=transaction)


@cashier_bp.route('/check-rentals', methods=['GET', 'POST'])
@login_required
@cashier_required
def check_rentals():
    """Check customer rental status."""
    rentals = []
    customer_phone = ''
    
    if request.method == 'POST':
        customer_phone = request.form.get('customer_phone', '').strip()
        if customer_phone:
            rentals = RentalService.get_rentals_by_customer(customer_phone)
            if not rentals:
                flash('No rentals found for this customer', 'info')
    
    return render_template('cashier/check_rentals.html', 
                          rentals=rentals, 
                          customer_phone=customer_phone)


@cashier_bp.route('/validate-coupon', methods=['POST'])
@login_required
@cashier_required
def validate_coupon():
    """AJAX endpoint to validate coupon code."""
    code = request.form.get('code', '')
    amount_str = request.form.get('amount', '0')
    
    # Handle empty string for amount
    try:
        amount = float(amount_str) if amount_str.strip() else 0.0
    except ValueError:
        amount = 0.0
    
    result = CouponService.validate_coupon(code, amount)
    
    if result['valid']:
        coupon = result['coupon']
        return jsonify({
            'valid': True,
            'discount': result['discount'],
            'discount_percent': coupon.discount_percent if coupon.discount_percent > 0 else 0,
            'discount_amount': coupon.discount_amount if coupon.discount_amount > 0 else 0,
            'message': result['message']
        })
    else:
        return jsonify({
            'valid': False,
            'message': result['message']
        })


@cashier_bp.route('/search-items')
@login_required
@cashier_required
def search_items():
    """AJAX endpoint to search items."""
    query = request.args.get('q', '')
    item_type = request.args.get('type', None)
    
    if len(query) < 2:
        return jsonify([])
    
    items = InventoryService.search_items(query, item_type)
    return jsonify([item.to_dict() for item in items])
