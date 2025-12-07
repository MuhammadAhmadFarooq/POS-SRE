"""
Admin Controller - Handles admin operations.
Replaces legacy Admin_Interface.java, AddEmployee_Interface.java, etc.
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from functools import wraps
from app.services.employee_service import EmployeeService, EmployeeError
from app.services.inventory_service import InventoryService, InventoryError
from app.services.transaction_service import TransactionService
from app.services.rental_service import RentalService
from app.services.coupon_service import CouponService, CouponError
from app.services.auth_service import AuthService
from app.models.employee import EmployeeRole
from app.models.item import ItemType

admin_bp = Blueprint('admin', __name__)


def admin_required(f):
    """Decorator to require admin or manager role."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login'))
        if not current_user.has_admin_access():
            flash('Access denied. Admin privileges required.', 'danger')
            return redirect(url_for('cashier.dashboard'))
        return f(*args, **kwargs)
    return decorated_function


@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    """Admin dashboard with statistics."""
    # Gather all stats
    employee_stats = EmployeeService.get_employee_stats()
    inventory_stats = InventoryService.get_inventory_stats()
    rental_stats = RentalService.get_rental_stats()
    daily_sales = TransactionService.get_daily_sales()
    coupon_stats = CouponService.get_coupon_stats()
    
    return render_template('admin/dashboard.html',
                          employee_stats=employee_stats,
                          inventory_stats=inventory_stats,
                          rental_stats=rental_stats,
                          daily_sales=daily_sales,
                          coupon_stats=coupon_stats)


# ============= EMPLOYEE MANAGEMENT =============

@admin_bp.route('/employees')
@login_required
@admin_required
def employees():
    """List all employees."""
    show_inactive = request.args.get('show_inactive', 'false') == 'true'
    employees = EmployeeService.get_all_employees(active_only=not show_inactive)
    return render_template('admin/employees/list.html', 
                          employees=employees, 
                          show_inactive=show_inactive)


@admin_bp.route('/employees/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_employee():
    """Add a new employee."""
    if request.method == 'POST':
        try:
            employee_id = request.form.get('employee_id', '').strip()
            username = request.form.get('username', '').strip()
            password = request.form.get('password', '')
            first_name = request.form.get('first_name', '').strip()
            last_name = request.form.get('last_name', '').strip()
            role = request.form.get('role', EmployeeRole.CASHIER)
            
            # Validate
            if not all([employee_id, username, password, first_name, last_name]):
                flash('All fields are required', 'warning')
                return render_template('admin/employees/add.html', roles=EmployeeRole.all_roles())
            
            employee = EmployeeService.create_employee(
                employee_id=employee_id,
                username=username,
                password=password,
                first_name=first_name,
                last_name=last_name,
                role=role
            )
            
            flash(f'Employee {employee.full_name} added successfully!', 'success')
            return redirect(url_for('admin.employees'))
            
        except EmployeeError as e:
            flash(str(e), 'danger')
    
    # Generate suggested employee ID
    suggested_id = EmployeeService.generate_employee_id()
    return render_template('admin/employees/add.html', 
                          roles=EmployeeRole.all_roles(),
                          suggested_id=suggested_id)


@admin_bp.route('/employees/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_employee(id):
    """Edit an employee."""
    employee = EmployeeService.get_employee(id)
    if not employee:
        flash('Employee not found', 'danger')
        return redirect(url_for('admin.employees'))
    
    if request.method == 'POST':
        try:
            first_name = request.form.get('first_name', '').strip()
            last_name = request.form.get('last_name', '').strip()
            role = request.form.get('role', employee.role)
            
            EmployeeService.update_employee(
                employee,
                first_name=first_name,
                last_name=last_name,
                role=role
            )
            
            flash('Employee updated successfully!', 'success')
            return redirect(url_for('admin.employees'))
            
        except EmployeeError as e:
            flash(str(e), 'danger')
    
    return render_template('admin/employees/edit.html', 
                          employee=employee, 
                          roles=EmployeeRole.all_roles())


@admin_bp.route('/employees/<int:id>/reset-password', methods=['POST'])
@login_required
@admin_required
def reset_employee_password(id):
    """Reset an employee's password."""
    employee = EmployeeService.get_employee(id)
    if not employee:
        flash('Employee not found', 'danger')
        return redirect(url_for('admin.employees'))
    
    new_password = request.form.get('new_password', '')
    if len(new_password) < 4:
        flash('Password must be at least 4 characters', 'warning')
        return redirect(url_for('admin.edit_employee', id=id))
    
    AuthService.reset_password(employee, new_password)
    flash(f'Password reset for {employee.full_name}', 'success')
    return redirect(url_for('admin.employees'))


@admin_bp.route('/employees/<int:id>/toggle-status', methods=['POST'])
@login_required
@admin_required
def toggle_employee_status(id):
    """Toggle employee active status."""
    employee = EmployeeService.get_employee(id)
    if not employee:
        flash('Employee not found', 'danger')
        return redirect(url_for('admin.employees'))
    
    if employee.is_active:
        EmployeeService.delete_employee(employee)
        flash(f'{employee.full_name} has been deactivated', 'info')
    else:
        EmployeeService.restore_employee(employee)
        flash(f'{employee.full_name} has been activated', 'success')
    
    return redirect(url_for('admin.employees'))


# ============= INVENTORY MANAGEMENT =============

@admin_bp.route('/inventory')
@login_required
@admin_required
def inventory():
    """List all inventory items."""
    item_type = request.args.get('type', None)
    show_inactive = request.args.get('show_inactive', 'false') == 'true'
    
    items = InventoryService.get_all_items(
        item_type=item_type, 
        active_only=not show_inactive
    )
    
    return render_template('admin/inventory/list.html', 
                          items=items, 
                          item_type=item_type,
                          show_inactive=show_inactive,
                          item_types=ItemType.all_types())


@admin_bp.route('/inventory/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_item():
    """Add a new inventory item."""
    if request.method == 'POST':
        try:
            item_id = request.form.get('item_id', '').strip()
            name = request.form.get('name', '').strip()
            price = float(request.form.get('price', 0))
            quantity = int(request.form.get('quantity', 0))
            item_type = request.form.get('item_type', ItemType.SALE)
            description = request.form.get('description', '').strip() or None
            
            # Validate
            if not all([item_id, name, price >= 0]):
                flash('Item ID, name, and valid price are required', 'warning')
                return render_template('admin/inventory/add.html', item_types=ItemType.all_types())
            
            item = InventoryService.add_item(
                item_id=item_id,
                name=name,
                price=price,
                quantity=quantity,
                item_type=item_type,
                description=description
            )
            
            flash(f'Item {item.name} added successfully!', 'success')
            return redirect(url_for('admin.inventory'))
            
        except InventoryError as e:
            flash(str(e), 'danger')
    
    return render_template('admin/inventory/add.html', item_types=ItemType.all_types())


@admin_bp.route('/inventory/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_item(id):
    """Edit an inventory item."""
    item = InventoryService.get_item(id)
    if not item:
        flash('Item not found', 'danger')
        return redirect(url_for('admin.inventory'))
    
    if request.method == 'POST':
        try:
            name = request.form.get('name', '').strip()
            price = float(request.form.get('price', 0))
            quantity = int(request.form.get('quantity', 0))
            description = request.form.get('description', '').strip() or None
            
            InventoryService.update_item(
                item,
                name=name,
                price=price,
                quantity=quantity,
                description=description
            )
            
            flash('Item updated successfully!', 'success')
            return redirect(url_for('admin.inventory'))
            
        except InventoryError as e:
            flash(str(e), 'danger')
    
    return render_template('admin/inventory/edit.html', item=item)


@admin_bp.route('/inventory/<int:id>/add-stock', methods=['POST'])
@login_required
@admin_required
def add_stock(id):
    """Add stock to an item."""
    item = InventoryService.get_item(id)
    if not item:
        flash('Item not found', 'danger')
        return redirect(url_for('admin.inventory'))
    
    try:
        amount = int(request.form.get('amount', 0))
        InventoryService.add_stock(item, amount)
        flash(f'Added {amount} units to {item.name}', 'success')
    except (ValueError, InventoryError) as e:
        flash(str(e), 'danger')
    
    return redirect(url_for('admin.inventory'))


@admin_bp.route('/inventory/<int:id>/toggle-status', methods=['POST'])
@login_required
@admin_required
def toggle_item_status(id):
    """Toggle item active status."""
    item = InventoryService.get_item(id)
    if not item:
        flash('Item not found', 'danger')
        return redirect(url_for('admin.inventory'))
    
    if item.is_active:
        InventoryService.deactivate_item(item)
        flash(f'{item.name} has been deactivated', 'info')
    else:
        InventoryService.activate_item(item)
        flash(f'{item.name} has been activated', 'success')
    
    return redirect(url_for('admin.inventory'))


# ============= REPORTS =============

@admin_bp.route('/reports')
@login_required
@admin_required
def reports():
    """Reports dashboard."""
    return render_template('admin/reports/index.html')


@admin_bp.route('/reports/transactions')
@login_required
@admin_required
def transaction_report():
    """Transaction report."""
    from datetime import datetime, timedelta
    
    # Get date range
    days = int(request.args.get('days', 7))
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    transactions = TransactionService.get_transactions(
        start_date=start_date,
        end_date=end_date,
        limit=500
    )
    
    # Calculate summaries
    total_sales = sum(t.total for t in transactions if t.is_sale())
    total_rentals = sum(t.total for t in transactions if t.is_rental())
    
    return render_template('admin/reports/transactions.html',
                          transactions=transactions,
                          total_sales=total_sales,
                          total_rentals=total_rentals,
                          days=days)


@admin_bp.route('/reports/low-stock')
@login_required
@admin_required
def low_stock_report():
    """Low stock report."""
    low_stock = InventoryService.get_low_stock_items()
    out_of_stock = InventoryService.get_out_of_stock_items()
    
    return render_template('admin/reports/low_stock.html',
                          low_stock=low_stock,
                          out_of_stock=out_of_stock)


@admin_bp.route('/reports/overdue-rentals')
@login_required
@admin_required
def overdue_rentals_report():
    """Overdue rentals report."""
    overdue = RentalService.get_overdue_rentals()
    due_soon = RentalService.get_due_soon_rentals(days=3)
    
    return render_template('admin/reports/overdue_rentals.html',
                          overdue=overdue,
                          due_soon=due_soon)


# ============= COUPONS =============

@admin_bp.route('/coupons')
@login_required
@admin_required
def coupons():
    """List all coupons."""
    coupons = CouponService.get_all_coupons()
    return render_template('admin/coupons/list.html', coupons=coupons)


@admin_bp.route('/coupons/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_coupon():
    """Add a new coupon."""
    if request.method == 'POST':
        try:
            code = request.form.get('code', '').strip().upper()
            discount_percent = float(request.form.get('discount_percent', 0))
            discount_amount = float(request.form.get('discount_amount', 0))
            description = request.form.get('description', '').strip() or None
            max_uses = request.form.get('max_uses', '')
            max_uses = int(max_uses) if max_uses else None
            minimum_purchase = float(request.form.get('minimum_purchase', 0))
            
            coupon = CouponService.create_coupon(
                code=code,
                discount_percent=discount_percent,
                discount_amount=discount_amount,
                description=description,
                max_uses=max_uses,
                minimum_purchase=minimum_purchase
            )
            
            flash(f'Coupon {coupon.code} created successfully!', 'success')
            return redirect(url_for('admin.coupons'))
            
        except CouponError as e:
            flash(str(e), 'danger')
    
    # Generate suggested code
    suggested_code = CouponService.generate_coupon_code()
    return render_template('admin/coupons/add.html', suggested_code=suggested_code)


@admin_bp.route('/coupons/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_coupon(id):
    """Edit an existing coupon."""
    coupon = CouponService.get_coupon(id)
    if not coupon:
        flash('Coupon not found', 'danger')
        return redirect(url_for('admin.coupons'))
    
    if request.method == 'POST':
        try:
            discount_percent = request.form.get('discount_percent', '')
            discount_amount = request.form.get('discount_amount', '')
            max_uses = request.form.get('max_uses', '')
            expires_at_str = request.form.get('expires_at', '')
            
            # Parse values
            discount_percent = float(discount_percent) if discount_percent else None
            discount_amount = float(discount_amount) if discount_amount else None
            max_uses = int(max_uses) if max_uses else None
            
            # Parse expiration date
            expires_at = None
            if expires_at_str:
                from datetime import datetime
                expires_at = datetime.strptime(expires_at_str, '%Y-%m-%d')
            
            CouponService.update_coupon(
                coupon,
                discount_percent=discount_percent,
                discount_amount=discount_amount,
                max_uses=max_uses,
                expires_at=expires_at
            )
            
            flash(f'Coupon {coupon.code} updated successfully!', 'success')
            return redirect(url_for('admin.coupons'))
            
        except (CouponError, ValueError) as e:
            flash(str(e), 'danger')
    
    return render_template('admin/coupons/edit.html', coupon=coupon)


@admin_bp.route('/coupons/<int:id>/toggle-status', methods=['POST'])
@login_required
@admin_required
def toggle_coupon_status(id):
    """Toggle coupon active status."""
    coupon = CouponService.get_coupon(id)
    if not coupon:
        flash('Coupon not found', 'danger')
        return redirect(url_for('admin.coupons'))
    
    if coupon.is_active:
        CouponService.deactivate_coupon(coupon)
        flash(f'Coupon {coupon.code} has been deactivated', 'info')
    else:
        CouponService.activate_coupon(coupon)
        flash(f'Coupon {coupon.code} has been activated', 'success')
    
    return redirect(url_for('admin.coupons'))
