"""
Seed the database with comprehensive test data.
Run this script to create users, items, customers, coupons and sample transactions.
"""
from datetime import datetime, timedelta
from app import create_app, db
from app.models.employee import Employee
from app.models.item import Item
from app.models.customer import Customer
from app.models.coupon import Coupon
from app.models.transaction import Transaction, TransactionItem
from app.models.rental import Rental

def seed_database():
    app = create_app()
    
    with app.app_context():
        print("=" * 50)
        print("🌱 SEEDING DATABASE WITH TEST DATA")
        print("=" * 50)
        
        # ============= EMPLOYEES =============
        print("\n📋 Creating Employees...")
        employees_data = [
            {'employee_id': 'EMP001', 'username': 'admin', 'password': 'admin123', 
             'first_name': 'Admin', 'last_name': 'User', 'role': 'admin'},
            {'employee_id': 'EMP002', 'username': 'manager', 'password': 'manager123', 
             'first_name': 'Sarah', 'last_name': 'Johnson', 'role': 'manager'},
            {'employee_id': 'EMP003', 'username': 'cashier1', 'password': 'cashier123', 
             'first_name': 'John', 'last_name': 'Doe', 'role': 'cashier'},
            {'employee_id': 'EMP004', 'username': 'cashier2', 'password': 'cashier123', 
             'first_name': 'Jane', 'last_name': 'Smith', 'role': 'cashier'},
        ]
        
        for emp_data in employees_data:
            existing = Employee.query.filter_by(username=emp_data['username']).first()
            existing_id = Employee.query.filter_by(employee_id=emp_data['employee_id']).first()
            if not existing and not existing_id:
                emp = Employee(**emp_data)
                db.session.add(emp)
                print(f"  ✓ Employee: {emp_data['first_name']} {emp_data['last_name']} ({emp_data['role']})")
            else:
                print(f"  - Skipped (exists): {emp_data['username']}")
        
        db.session.commit()
        
        # ============= SALE ITEMS =============
        print("\n🛒 Creating Sale Items...")
        sale_items = [
            {'item_id': 'SAL001', 'name': 'Coffee Mug', 'price': 9.99, 'quantity': 50, 'item_type': 'sale', 'description': 'Ceramic coffee mug, 12oz'},
            {'item_id': 'SAL002', 'name': 'T-Shirt (M)', 'price': 19.99, 'quantity': 100, 'item_type': 'sale', 'description': 'Cotton t-shirt, medium size'},
            {'item_id': 'SAL003', 'name': 'T-Shirt (L)', 'price': 19.99, 'quantity': 80, 'item_type': 'sale', 'description': 'Cotton t-shirt, large size'},
            {'item_id': 'SAL004', 'name': 'Notebook', 'price': 4.99, 'quantity': 200, 'item_type': 'sale', 'description': '100-page ruled notebook'},
            {'item_id': 'SAL005', 'name': 'Pen Set', 'price': 7.99, 'quantity': 150, 'item_type': 'sale', 'description': 'Set of 5 ballpoint pens'},
            {'item_id': 'SAL006', 'name': 'Water Bottle', 'price': 14.99, 'quantity': 75, 'item_type': 'sale', 'description': 'Stainless steel, 500ml'},
            {'item_id': 'SAL007', 'name': 'Backpack', 'price': 39.99, 'quantity': 30, 'item_type': 'sale', 'description': 'Laptop backpack with multiple compartments'},
            {'item_id': 'SAL008', 'name': 'Mouse Pad', 'price': 12.99, 'quantity': 120, 'item_type': 'sale', 'description': 'Large gaming mouse pad'},
            {'item_id': 'SAL009', 'name': 'USB Cable', 'price': 8.99, 'quantity': 200, 'item_type': 'sale', 'description': 'USB-C to USB-A, 6ft'},
            {'item_id': 'SAL010', 'name': 'Headphones', 'price': 29.99, 'quantity': 45, 'item_type': 'sale', 'description': 'Over-ear wired headphones'},
            {'item_id': 'SAL011', 'name': 'Desk Lamp', 'price': 24.99, 'quantity': 25, 'item_type': 'sale', 'description': 'LED desk lamp with adjustable brightness'},
            {'item_id': 'SAL012', 'name': 'Phone Stand', 'price': 15.99, 'quantity': 60, 'item_type': 'sale', 'description': 'Adjustable phone/tablet stand'},
            {'item_id': 'LOW001', 'name': 'Limited Edition Poster', 'price': 49.99, 'quantity': 3, 'item_type': 'sale', 'description': 'Collector item - LOW STOCK'},
            {'item_id': 'OUT001', 'name': 'Vintage Clock', 'price': 89.99, 'quantity': 0, 'item_type': 'sale', 'description': 'OUT OF STOCK - Retro wall clock'},
        ]
        
        for item_data in sale_items:
            existing = Item.query.filter_by(item_id=item_data['item_id']).first()
            if not existing:
                item = Item(**item_data)
                db.session.add(item)
                print(f"  ✓ Sale Item: {item_data['name']} (${item_data['price']}) - Qty: {item_data['quantity']}")
        
        # ============= RENTAL ITEMS =============
        print("\n📦 Creating Rental Items...")
        rental_items = [
            {'item_id': 'RNT001', 'name': 'DVD Player', 'price': 5.00, 'quantity': 10, 'item_type': 'rental', 'description': 'DVD/Blu-ray player - $5/day'},
            {'item_id': 'RNT002', 'name': 'Projector', 'price': 25.00, 'quantity': 5, 'item_type': 'rental', 'description': 'HD Projector with HDMI - $25/day'},
            {'item_id': 'RNT003', 'name': 'Camera (DSLR)', 'price': 35.00, 'quantity': 8, 'item_type': 'rental', 'description': 'Professional DSLR camera - $35/day'},
            {'item_id': 'RNT004', 'name': 'Tripod', 'price': 8.00, 'quantity': 15, 'item_type': 'rental', 'description': 'Camera tripod - $8/day'},
            {'item_id': 'RNT005', 'name': 'Microphone Kit', 'price': 15.00, 'quantity': 6, 'item_type': 'rental', 'description': 'Wireless microphone set - $15/day'},
            {'item_id': 'RNT006', 'name': 'Speaker System', 'price': 40.00, 'quantity': 4, 'item_type': 'rental', 'description': 'Portable PA system - $40/day'},
            {'item_id': 'RNT007', 'name': 'Laptop', 'price': 30.00, 'quantity': 10, 'item_type': 'rental', 'description': 'Business laptop - $30/day'},
            {'item_id': 'RNT008', 'name': 'Gaming Console', 'price': 20.00, 'quantity': 5, 'item_type': 'rental', 'description': 'Game console with controllers - $20/day'},
        ]
        
        for item_data in rental_items:
            existing = Item.query.filter_by(item_id=item_data['item_id']).first()
            if not existing:
                item = Item(**item_data)
                db.session.add(item)
                print(f"  ✓ Rental Item: {item_data['name']} (${item_data['price']}/day) - Qty: {item_data['quantity']}")
        
        db.session.commit()
        
        # ============= CUSTOMERS =============
        print("\n👥 Creating Customers...")
        customers_data = [
            {'phone': '555-0101', 'name': 'Alice Brown', 'email': 'alice.brown@email.com', 'address': '123 Main St, City'},
            {'phone': '555-0102', 'name': 'Bob Wilson', 'email': 'bob.wilson@email.com', 'address': '456 Oak Ave, Town'},
            {'phone': '555-0103', 'name': 'Carol Davis', 'email': 'carol.davis@email.com', 'address': '789 Pine Rd, Village'},
            {'phone': '555-0104', 'name': 'David Miller', 'email': 'david.miller@email.com', 'address': '321 Elm Blvd, City'},
            {'phone': '555-0105', 'name': 'Eva Martinez', 'email': 'eva.martinez@email.com', 'address': '654 Cedar Ln, Town'},
            {'phone': '555-0106', 'name': 'Frank Garcia', 'email': 'frank.garcia@email.com', 'address': '987 Birch St, Village'},
            {'phone': '555-0107', 'name': 'Grace Lee', 'email': 'grace.lee@email.com', 'address': '147 Maple Dr, City'},
            {'phone': '555-0108', 'name': 'Henry Taylor', 'email': 'henry.taylor@email.com', 'address': '258 Walnut Way, Town'},
        ]
        
        for cust_data in customers_data:
            existing = Customer.query.filter_by(phone=cust_data['phone']).first()
            if not existing:
                customer = Customer(**cust_data)
                db.session.add(customer)
                print(f"  ✓ Customer: {cust_data['name']} ({cust_data['phone']})")
        
        db.session.commit()
        
        # ============= COUPONS =============
        print("\n🎟️ Creating Coupons...")
        coupons_data = [
            {'code': 'SAVE10', 'discount_percent': 10, 'description': '10% off your purchase', 'max_uses': 100},
            {'code': 'SAVE20', 'discount_percent': 20, 'description': '20% off your purchase', 'max_uses': 50},
            {'code': 'FLAT5', 'discount_amount': 5.00, 'description': '$5 off any purchase', 'max_uses': 200},
            {'code': 'FLAT10', 'discount_amount': 10.00, 'description': '$10 off purchases over $50', 'minimum_purchase': 50.00, 'max_uses': 100},
            {'code': 'WELCOME', 'discount_percent': 15, 'description': '15% off for new customers', 'max_uses': 500},
            {'code': 'VIP25', 'discount_percent': 25, 'description': 'VIP 25% discount', 'max_uses': 25},
            {'code': 'EXPIRED', 'discount_percent': 50, 'description': 'Expired coupon for testing', 'expires_at': datetime.utcnow() - timedelta(days=30)},
        ]
        
        for coupon_data in coupons_data:
            existing = Coupon.query.filter_by(code=coupon_data['code']).first()
            if not existing:
                coupon = Coupon(**coupon_data)
                db.session.add(coupon)
                discount = f"{coupon_data.get('discount_percent', '')}%" if coupon_data.get('discount_percent') else f"${coupon_data.get('discount_amount', '')}"
                print(f"  ✓ Coupon: {coupon_data['code']} - {discount} off")
        
        db.session.commit()
        
        # ============= SAMPLE RENTALS (for testing returns) =============
        print("\n📋 Creating Sample Rentals...")
        
        # Get references
        cashier = Employee.query.filter_by(username='cashier1').first()
        alice = Customer.query.filter_by(phone='555-0101').first()
        bob = Customer.query.filter_by(phone='555-0102').first()
        carol = Customer.query.filter_by(phone='555-0103').first()
        
        projector = Item.query.filter_by(item_id='RNT002').first()
        camera = Item.query.filter_by(item_id='RNT003').first()
        laptop = Item.query.filter_by(item_id='RNT007').first()
        
        if cashier and alice and projector:
            # Active rental (due in 3 days)
            existing_rental = Rental.query.filter_by(customer_id=alice.id, item_id=projector.id, returned=False).first()
            if not existing_rental:
                rental1 = Rental(
                    customer_id=alice.id,
                    item_id=projector.id,
                    quantity=1,
                    rental_price=projector.price,
                    rental_days=7  # 7 day rental
                )
                # Adjust dates for testing
                rental1.rental_date = datetime.utcnow() - timedelta(days=4)
                rental1.due_date = datetime.utcnow() + timedelta(days=3)
                db.session.add(rental1)
                print(f"  ✓ Active Rental: {alice.name} - {projector.name} (due in 3 days)")
        
        if cashier and bob and camera:
            # Overdue rental
            existing_rental = Rental.query.filter_by(customer_id=bob.id, item_id=camera.id, returned=False).first()
            if not existing_rental:
                rental2 = Rental(
                    customer_id=bob.id,
                    item_id=camera.id,
                    quantity=1,
                    rental_price=camera.price,
                    rental_days=7  # 7 day rental
                )
                # Adjust dates to make it overdue
                rental2.rental_date = datetime.utcnow() - timedelta(days=10)
                rental2.due_date = datetime.utcnow() - timedelta(days=3)
                db.session.add(rental2)
                print(f"  ✓ OVERDUE Rental: {bob.name} - {camera.name} (3 days overdue!)")
        
        if cashier and carol and laptop:
            # Due today
            existing_rental = Rental.query.filter_by(customer_id=carol.id, item_id=laptop.id, returned=False).first()
            if not existing_rental:
                rental3 = Rental(
                    customer_id=carol.id,
                    item_id=laptop.id,
                    quantity=1,
                    rental_price=laptop.price,
                    rental_days=7  # 7 day rental
                )
                # Adjust dates to make it due today
                rental3.rental_date = datetime.utcnow() - timedelta(days=7)
                rental3.due_date = datetime.utcnow()
                db.session.add(rental3)
                print(f"  ✓ Due Today: {carol.name} - {laptop.name}")
        
        db.session.commit()
        
        # ============= SUMMARY =============
        print("\n" + "=" * 50)
        print("✅ DATABASE SEEDED SUCCESSFULLY!")
        print("=" * 50)
        
        print("\n📊 SUMMARY:")
        print(f"  • Employees: {Employee.query.count()}")
        print(f"  • Items: {Item.query.count()} ({Item.query.filter_by(item_type='sale').count()} sale, {Item.query.filter_by(item_type='rental').count()} rental)")
        print(f"  • Customers: {Customer.query.count()}")
        print(f"  • Coupons: {Coupon.query.count()}")
        print(f"  • Active Rentals: {Rental.query.filter_by(returned=False).count()}")
        
        print("\n🔐 LOGIN CREDENTIALS:")
        print("  ┌─────────────┬─────────────┬──────────────┐")
        print("  │ Role        │ Username    │ Password     │")
        print("  ├─────────────┼─────────────┼──────────────┤")
        print("  │ Admin       │ admin       │ admin123     │")
        print("  │ Manager     │ manager     │ manager123   │")
        print("  │ Cashier     │ cashier1    │ cashier123   │")
        print("  │ Cashier     │ cashier2    │ cashier123   │")
        print("  └─────────────┴─────────────┴──────────────┘")
        
        print("\n🎟️ TEST COUPONS:")
        print("  • SAVE10 - 10% off")
        print("  • SAVE20 - 20% off")
        print("  • FLAT5  - $5 off")
        print("  • FLAT10 - $10 off (min $50 purchase)")
        print("  • WELCOME - 15% off")
        print("  • VIP25  - 25% off")
        
        print("\n👥 TEST CUSTOMERS (for rentals):")
        print("  • 555-0101 - Alice Brown (has active rental)")
        print("  • 555-0102 - Bob Wilson (has OVERDUE rental)")
        print("  • 555-0103 - Carol Davis (rental due today)")
        print("  • 555-0104 to 555-0108 - More test customers")
        
        print("\n🚀 Ready to test at: http://127.0.0.1:5000")

if __name__ == '__main__':
    seed_database()
