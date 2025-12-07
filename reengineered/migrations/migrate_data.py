"""
Data Migration Script
Migrates data from legacy text files to SQLite database.

This script reads the legacy text file databases and populates
the new SQLAlchemy-based database with the migrated data.
"""
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models.employee import Employee, EmployeeRole
from app.models.item import Item, ItemType
from app.models.customer import Customer
from app.models.coupon import Coupon


def get_legacy_path(filename):
    """Get path to legacy database file."""
    base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    return os.path.join(base_path, 'Database', filename)


def migrate_employees():
    """
    Migrate employees from employeeDatabase.txt
    
    Legacy format: ID Position FirstName LastName Password
    Example: 2001 Cashier John Doe password
    """
    print("\n=== Migrating Employees ===")
    filepath = get_legacy_path('employeeDatabase.txt')
    
    if not os.path.exists(filepath):
        print(f"  Warning: {filepath} not found")
        return
    
    migrated = 0
    skipped = 0
    
    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            
            parts = line.split()
            if len(parts) < 5:
                print(f"  Skipping invalid line: {line}")
                skipped += 1
                continue
            
            employee_id = parts[0]
            position = parts[1]
            first_name = parts[2]
            last_name = parts[3]
            password = parts[4]
            
            # Map position to role
            role = EmployeeRole.CASHIER
            if position.lower() == 'admin':
                role = EmployeeRole.ADMIN
            elif position.lower() == 'manager':
                role = EmployeeRole.MANAGER
            
            # Check if already exists
            if Employee.query.filter_by(employee_id=employee_id).first():
                print(f"  Skipping existing: {employee_id}")
                skipped += 1
                continue
            
            # Create username from employee_id
            username = f"emp{employee_id}"
            
            employee = Employee(
                employee_id=employee_id,
                username=username,
                password=password,  # Will be hashed by model
                first_name=first_name,
                last_name=last_name,
                role=role
            )
            db.session.add(employee)
            migrated += 1
            print(f"  Migrated: {employee_id} - {first_name} {last_name} ({role})")
    
    db.session.commit()
    print(f"  Total: {migrated} migrated, {skipped} skipped")


def migrate_items(filename, item_type):
    """
    Migrate items from text file.
    
    Legacy format: ItemID ItemName Price Quantity
    Example: A001 Widget 9.99 50
    """
    print(f"\n=== Migrating Items ({item_type}) ===")
    filepath = get_legacy_path(filename)
    
    if not os.path.exists(filepath):
        print(f"  Warning: {filepath} not found")
        return
    
    migrated = 0
    skipped = 0
    
    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            
            parts = line.split()
            if len(parts) < 4:
                print(f"  Skipping invalid line: {line}")
                skipped += 1
                continue
            
            item_id = parts[0]
            name = ' '.join(parts[1:-2])  # Name might have spaces
            
            try:
                price = float(parts[-2])
                quantity = int(parts[-1])
            except ValueError:
                # Try alternative parsing
                try:
                    price = float(parts[2])
                    quantity = int(parts[3])
                    name = parts[1]
                except ValueError:
                    print(f"  Skipping unparseable line: {line}")
                    skipped += 1
                    continue
            
            # Check if already exists
            if Item.query.filter_by(item_id=item_id).first():
                print(f"  Skipping existing: {item_id}")
                skipped += 1
                continue
            
            item = Item(
                item_id=item_id,
                name=name,
                price=price,
                quantity=quantity,
                item_type=item_type
            )
            db.session.add(item)
            migrated += 1
    
    db.session.commit()
    print(f"  Total: {migrated} migrated, {skipped} skipped")


def migrate_customers():
    """
    Migrate customers from userDatabase.txt
    
    Legacy format: PhoneNumber RentalInfo1 RentalInfo2...
    Example: 555-1234 ItemA001_2023-01-15
    """
    print("\n=== Migrating Customers ===")
    filepath = get_legacy_path('userDatabase.txt')
    
    if not os.path.exists(filepath):
        print(f"  Warning: {filepath} not found")
        return
    
    migrated = 0
    skipped = 0
    
    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            
            parts = line.split()
            if len(parts) < 1:
                continue
            
            phone = parts[0]
            
            # Check if already exists
            if Customer.query.filter_by(phone=phone).first():
                skipped += 1
                continue
            
            customer = Customer(phone=phone)
            db.session.add(customer)
            migrated += 1
    
    db.session.commit()
    print(f"  Total: {migrated} migrated, {skipped} skipped")


def migrate_coupons():
    """
    Migrate coupons from couponNumber.txt
    
    Legacy format: One coupon code per line
    Example: C001
    """
    print("\n=== Migrating Coupons ===")
    filepath = get_legacy_path('couponNumber.txt')
    
    if not os.path.exists(filepath):
        print(f"  Warning: {filepath} not found")
        return
    
    migrated = 0
    skipped = 0
    
    with open(filepath, 'r') as f:
        for line in f:
            code = line.strip()
            if not code:
                continue
            
            # Check if already exists
            if Coupon.query.filter_by(code=code).first():
                skipped += 1
                continue
            
            # Default 10% discount for migrated coupons
            coupon = Coupon(
                code=code,
                discount_percent=10.0,
                description=f"Migrated coupon from legacy system"
            )
            db.session.add(coupon)
            migrated += 1
    
    db.session.commit()
    print(f"  Total: {migrated} migrated, {skipped} skipped")


def create_default_admin():
    """Create a default admin user if none exists."""
    print("\n=== Creating Default Admin ===")
    
    admin = Employee.query.filter_by(role=EmployeeRole.ADMIN).first()
    if admin:
        print(f"  Admin already exists: {admin.username}")
        return
    
    admin = Employee(
        employee_id='ADMIN001',
        username='admin',
        password='admin123',
        first_name='System',
        last_name='Administrator',
        role=EmployeeRole.ADMIN
    )
    db.session.add(admin)
    db.session.commit()
    print("  Created default admin:")
    print("    Username: admin")
    print("    Password: admin123")
    print("  (Please change this password after first login)")


def run_migration():
    """Run the complete data migration."""
    print("=" * 50)
    print("POS System Data Migration")
    print("Legacy Text Files -> SQLite Database")
    print("=" * 50)
    
    # Create Flask app context
    app = create_app('development')
    
    with app.app_context():
        # Create all tables
        print("\nCreating database tables...")
        db.create_all()
        
        # Run migrations
        migrate_employees()
        migrate_items('itemDatabase.txt', ItemType.SALE)
        migrate_items('rentalDatabase.txt', ItemType.RENTAL)
        migrate_customers()
        migrate_coupons()
        create_default_admin()
        
        print("\n" + "=" * 50)
        print("Migration Complete!")
        print("=" * 50)
        
        # Summary
        print("\nDatabase Summary:")
        print(f"  Employees: {Employee.query.count()}")
        print(f"  Items: {Item.query.count()}")
        print(f"  Customers: {Customer.query.count()}")
        print(f"  Coupons: {Coupon.query.count()}")


if __name__ == '__main__':
    run_migration()
