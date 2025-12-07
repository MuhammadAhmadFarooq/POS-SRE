# Data Restructuring Documentation

## Phase 5: Data Restructuring

This document details the data restructuring phase of the POS system reengineering project, covering the transformation from text file-based storage to a proper relational database.

---

## 1. Legacy Data Analysis

### 1.1 Original Data Files

| File | Format | Records | Purpose |
|------|--------|---------|---------|
| `employeeDatabase.txt` | Pipe-delimited | 5+ | Employee records |
| `itemDatabase.txt` | Pipe-delimited | 50+ | Product catalog |
| `userDatabase.txt` | Pipe-delimited | 10+ | Customer data |
| `rentalDatabase.txt` | Pipe-delimited | Variable | Active rentals |
| `saleInvoiceRecord.txt` | Pipe-delimited | Variable | Transaction history |
| `couponNumber.txt` | Plain text | 1 | Coupon counter |
| `employeeLogfile.txt` | Pipe-delimited | Variable | Audit log |
| `returnSale.txt` | Pipe-delimited | Variable | Return records |

### 1.2 Data Smells Identified

#### 🔴 Critical Issues

**1. Plain Text Passwords**
```
# employeeDatabase.txt
E001|admin|password123|John|Doe|Admin|...
```
- Passwords stored as plain text
- No hashing or encryption
- Critical security vulnerability

**2. No Data Validation**
- No type checking on values
- No range validation
- Corrupt data possible

#### 🟠 High Severity Issues

**3. No Referential Integrity**
```
# rentalDatabase.txt might reference:
R001|E001|I005|C001|...  # What if I005 is deleted?
```
- No foreign key constraints
- Orphaned records possible
- Inconsistent data states

**4. No Transaction Support**
- Partial writes on crash
- No rollback capability
- Data corruption risk

#### 🟡 Medium Severity Issues

**5. Inconsistent Date Formats**
```
# Different files use different formats:
2024-01-15        # ISO format
01/15/2024        # US format
15-Jan-2024       # Mixed format
```

**6. No Indexing**
- Linear search required (O(n))
- Poor performance with growth
- No unique constraints

---

## 2. Database Schema Design

### 2.1 Entity-Relationship Diagram

```
                                    ┌─────────────────┐
                                    │     Coupon      │
                                    ├─────────────────┤
                                    │ PK id           │
                                    │    code         │
                                    │    discount_%   │
                                    │    discount_$   │
                                    │    min_purchase │
                                    │    max_uses     │
                                    │    times_used   │
                                    │    is_active    │
                                    │    expires_at   │
                                    │    created_at   │
                                    └────────┬────────┘
                                             │
                                             │ 0..1
                                             │
┌─────────────────┐                ┌─────────▼─────────┐                ┌─────────────────┐
│    Employee     │                │   Transaction     │                │    Customer     │
├─────────────────┤                ├───────────────────┤                ├─────────────────┤
│ PK id           │                │ PK id             │                │ PK id           │
│    employee_id  │◄───────────────│ FK employee_id    │                │    phone        │
│    username     │      1..n      │ FK customer_id    │───────────────►│    name         │
│    password_hash│                │ FK coupon_id      │      0..n      │    email        │
│    first_name   │                │    txn_number     │                │    address      │
│    last_name    │                │    txn_type       │                │    is_active    │
│    role         │                │    subtotal       │                │    created_at   │
│    is_active    │                │    discount_amt   │                └────────┬────────┘
│    last_login   │                │    tax_amount     │                         │
│    created_at   │                │    total          │                         │
└─────────────────┘                │    payment_method │                         │
                                   │    amount_tender  │                         │
                                   │    change_given   │                         │
                                   │    created_at     │                         │
                                   └─────────┬─────────┘                         │
                                             │                                   │
                                             │ 1                                 │
                                             │                                   │
                                   ┌─────────▼─────────┐               ┌─────────▼─────────┐
                                   │ TransactionItem   │               │      Rental       │
                                   ├───────────────────┤               ├───────────────────┤
                                   │ PK id             │               │ PK id             │
                                   │ FK transaction_id │               │ FK customer_id    │
                                   │ FK item_id        │◄──────────────│ FK item_id        │
                                   │    quantity       │      0..n     │ FK transaction_id │
                                   │    unit_price     │               │    quantity       │
                                   └─────────┬─────────┘               │    rental_price   │
                                             │                         │    rental_date    │
                                             │ n                       │    due_date       │
                                             │                         │    returned       │
                                   ┌─────────▼─────────┐               │    return_date    │
                                   │       Item        │               │    late_fee       │
                                   ├───────────────────┤               │    notes          │
                                   │ PK id             │◄──────────────┴───────────────────┘
                                   │    item_id        │      0..n
                                   │    name           │
                                   │    price          │
                                   │    quantity       │
                                   │    item_type      │
                                   │    description    │
                                   │    is_active      │
                                   │    low_stock_thres│
                                   │    created_at     │
                                   └───────────────────┘
```

### 2.2 Table Definitions

#### employees Table

```sql
CREATE TABLE employees (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    employee_id VARCHAR(10) UNIQUE NOT NULL,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    role VARCHAR(20) DEFAULT 'Cashier' CHECK (role IN ('Admin', 'Manager', 'Cashier')),
    is_active BOOLEAN DEFAULT TRUE,
    last_login DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_employee_username (username),
    INDEX idx_employee_role (role)
);
```

#### items Table

```sql
CREATE TABLE items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_id VARCHAR(10) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    price FLOAT NOT NULL CHECK (price >= 0),
    quantity INTEGER DEFAULT 0 CHECK (quantity >= 0),
    item_type VARCHAR(20) DEFAULT 'sale' CHECK (item_type IN ('sale', 'rental')),
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    low_stock_threshold INTEGER DEFAULT 10 CHECK (low_stock_threshold >= 0),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_item_type (item_type),
    INDEX idx_item_active (is_active)
);
```

#### customers Table

```sql
CREATE TABLE customers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    phone VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(100),
    email VARCHAR(100),
    address TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_customer_phone (phone)
);
```

#### transactions Table

```sql
CREATE TABLE transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    transaction_number VARCHAR(20) UNIQUE NOT NULL,
    transaction_type VARCHAR(20) NOT NULL CHECK (transaction_type IN ('sale', 'rental', 'return')),
    employee_id INTEGER NOT NULL,
    customer_id INTEGER,
    coupon_id INTEGER,
    subtotal FLOAT DEFAULT 0 CHECK (subtotal >= 0),
    discount_amount FLOAT DEFAULT 0 CHECK (discount_amount >= 0),
    tax_amount FLOAT DEFAULT 0 CHECK (tax_amount >= 0),
    total FLOAT NOT NULL CHECK (total >= 0),
    payment_method VARCHAR(20) DEFAULT 'cash' CHECK (payment_method IN ('cash', 'credit', 'debit', 'check')),
    amount_tendered FLOAT DEFAULT 0 CHECK (amount_tendered >= 0),
    change_given FLOAT DEFAULT 0 CHECK (change_given >= 0),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (employee_id) REFERENCES employees(id),
    FOREIGN KEY (customer_id) REFERENCES customers(id),
    FOREIGN KEY (coupon_id) REFERENCES coupons(id),
    
    INDEX idx_txn_type (transaction_type),
    INDEX idx_txn_date (created_at),
    INDEX idx_txn_employee (employee_id)
);
```

#### transaction_items Table

```sql
CREATE TABLE transaction_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    transaction_id INTEGER NOT NULL,
    item_id INTEGER NOT NULL,
    quantity INTEGER DEFAULT 1 CHECK (quantity > 0),
    unit_price FLOAT NOT NULL CHECK (unit_price >= 0),
    
    FOREIGN KEY (transaction_id) REFERENCES transactions(id) ON DELETE CASCADE,
    FOREIGN KEY (item_id) REFERENCES items(id),
    
    INDEX idx_txn_items_txn (transaction_id),
    INDEX idx_txn_items_item (item_id)
);
```

#### rentals Table

```sql
CREATE TABLE rentals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER NOT NULL,
    item_id INTEGER NOT NULL,
    transaction_id INTEGER,
    quantity INTEGER DEFAULT 1 CHECK (quantity > 0),
    rental_price FLOAT NOT NULL CHECK (rental_price >= 0),
    rental_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    due_date DATETIME NOT NULL,
    returned BOOLEAN DEFAULT FALSE,
    return_date DATETIME,
    late_fee FLOAT DEFAULT 0 CHECK (late_fee >= 0),
    notes TEXT,
    
    FOREIGN KEY (customer_id) REFERENCES customers(id),
    FOREIGN KEY (item_id) REFERENCES items(id),
    FOREIGN KEY (transaction_id) REFERENCES transactions(id),
    
    INDEX idx_rental_customer (customer_id),
    INDEX idx_rental_item (item_id),
    INDEX idx_rental_returned (returned),
    INDEX idx_rental_due (due_date)
);
```

#### coupons Table

```sql
CREATE TABLE coupons (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code VARCHAR(20) UNIQUE NOT NULL,
    description VARCHAR(200),
    discount_percent FLOAT DEFAULT 0 CHECK (discount_percent >= 0 AND discount_percent <= 100),
    discount_amount FLOAT DEFAULT 0 CHECK (discount_amount >= 0),
    minimum_purchase FLOAT DEFAULT 0 CHECK (minimum_purchase >= 0),
    max_uses INTEGER,
    times_used INTEGER DEFAULT 0 CHECK (times_used >= 0),
    is_active BOOLEAN DEFAULT TRUE,
    expires_at DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_coupon_code (code),
    INDEX idx_coupon_active (is_active)
);
```

---

## 3. Data Migration

### 3.1 Migration Strategy

```
┌──────────────────┐     ┌──────────────────┐     ┌──────────────────┐
│   Legacy Files   │────►│ Migration Script │────►│  SQLite Database │
│   (Text Files)   │     │   (Python)       │     │   (Normalized)   │
└──────────────────┘     └──────────────────┘     └──────────────────┘
        │                         │                        │
        ▼                         ▼                        ▼
  ┌───────────┐           ┌───────────────┐        ┌───────────────┐
  │ Parse     │           │ Transform     │        │ Validate      │
  │ - Split   │           │ - Hash pwds   │        │ - Constraints │
  │ - Type    │           │ - Map IDs     │        │ - Integrity   │
  │   convert │           │ - Normalize   │        │ - Indexes     │
  └───────────┘           └───────────────┘        └───────────────┘
```

### 3.2 Migration Script

The migration script (`migrations/migrate_data.py`) handles:

1. **Employee Migration**
   - Parse `employeeDatabase.txt`
   - Hash plain text passwords with PBKDF2
   - Generate unique employee IDs if missing
   - Map roles to valid enum values

2. **Item Migration**
   - Parse `itemDatabase.txt`
   - Validate price and quantity values
   - Determine item type (sale/rental)
   - Set default stock thresholds

3. **Customer Migration**
   - Parse `userDatabase.txt`
   - Normalize phone numbers
   - Handle missing optional fields

4. **Transaction Migration**
   - Parse `saleInvoiceRecord.txt`
   - Link to employees and customers
   - Calculate subtotals and taxes
   - Create transaction items

5. **Rental Migration**
   - Parse `rentalDatabase.txt`
   - Link to customers and items
   - Calculate due dates
   - Flag overdue rentals

### 3.3 Data Transformation Rules

| Field | Legacy | Transformed |
|-------|--------|-------------|
| Password | Plain text | PBKDF2-SHA256 hash |
| Date | Various formats | ISO 8601 datetime |
| Price | String | Float (2 decimal) |
| Quantity | String | Integer |
| Boolean | "true"/"false" | SQLite BOOLEAN |
| Phone | Unformatted | Normalized string |
| Role | Mixed case | Standardized enum |

---

## 4. Security Improvements

### 4.1 Password Hashing

**Before (Legacy):**
```
E001|admin|password123|John|Doe|Admin
```

**After (Reengineered):**
```python
# Employee model with password hashing
from werkzeug.security import generate_password_hash, check_password_hash

class Employee(db.Model):
    password_hash = db.Column(db.String(255), nullable=False)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(
            password, 
            method='pbkdf2:sha256',
            salt_length=16
        )
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
```

### 4.2 Input Validation

```python
# SQLAlchemy validators
from sqlalchemy.orm import validates

class Item(db.Model):
    price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, default=0)
    
    @validates('price')
    def validate_price(self, key, price):
        if price < 0:
            raise ValueError("Price cannot be negative")
        return round(price, 2)
    
    @validates('quantity')
    def validate_quantity(self, key, quantity):
        if quantity < 0:
            raise ValueError("Quantity cannot be negative")
        return quantity
```

### 4.3 Foreign Key Constraints

```python
# SQLAlchemy relationships with constraints
class Transaction(db.Model):
    employee_id = db.Column(
        db.Integer, 
        db.ForeignKey('employees.id', ondelete='RESTRICT'),
        nullable=False
    )
    customer_id = db.Column(
        db.Integer, 
        db.ForeignKey('customers.id', ondelete='SET NULL'),
        nullable=True
    )
```

---

## 5. Performance Optimizations

### 5.1 Indexing Strategy

| Table | Index | Columns | Purpose |
|-------|-------|---------|---------|
| employees | idx_employee_username | username | Login lookup |
| employees | idx_employee_role | role | Role filtering |
| items | idx_item_type | item_type | Type filtering |
| items | idx_item_active | is_active | Active filter |
| transactions | idx_txn_date | created_at | Date range queries |
| transactions | idx_txn_type | transaction_type | Type filtering |
| rentals | idx_rental_due | due_date | Overdue check |
| rentals | idx_rental_returned | returned | Active rentals |

### 5.2 Query Optimization

**Before (Legacy - O(n) search):**
```java
// Linear scan of text file
for (String line : Files.readAllLines(path)) {
    String[] parts = line.split("\\|");
    if (parts[0].equals(searchId)) {
        return parts;
    }
}
```

**After (Reengineered - O(log n) with index):**
```python
# Indexed database query
item = Item.query.filter_by(item_id=search_id).first()
```

---

## 6. Verification

### 6.1 Migration Verification Queries

```sql
-- Verify employee count
SELECT COUNT(*) FROM employees;

-- Verify no plain text passwords
SELECT COUNT(*) FROM employees WHERE password_hash NOT LIKE 'pbkdf2:sha256:%';

-- Verify referential integrity
SELECT t.id FROM transactions t 
LEFT JOIN employees e ON t.employee_id = e.id 
WHERE e.id IS NULL;

-- Verify item quantities
SELECT * FROM items WHERE quantity < 0;

-- Verify rental dates
SELECT * FROM rentals WHERE due_date < rental_date;
```

### 6.2 Data Integrity Checks

```python
# Migration verification
def verify_migration():
    # Check employee passwords are hashed
    for emp in Employee.query.all():
        assert emp.password_hash.startswith('pbkdf2:sha256:')
    
    # Check all transactions have valid employee
    for txn in Transaction.query.all():
        assert txn.employee is not None
    
    # Check all rentals have valid customer and item
    for rental in Rental.query.all():
        assert rental.customer is not None
        assert rental.item is not None
    
    print("Migration verification passed!")
```

---

## 7. Summary

### Data Restructuring Achievements

| Aspect | Legacy | Reengineered |
|--------|--------|--------------|
| Storage | 11 text files | 7 normalized tables |
| Security | Plain text | PBKDF2 hashing |
| Integrity | None | Foreign keys + constraints |
| Validation | None | Type + range validation |
| Performance | O(n) | O(log n) with indexes |
| Transactions | None | SQLite ACID |
| Backup | File copy | Database dump |

### Files Created

- `app/models/employee.py` - Employee SQLAlchemy model
- `app/models/item.py` - Item SQLAlchemy model
- `app/models/customer.py` - Customer SQLAlchemy model
- `app/models/transaction.py` - Transaction + TransactionItem models
- `app/models/rental.py` - Rental SQLAlchemy model
- `app/models/coupon.py` - Coupon SQLAlchemy model
- `migrations/migrate_data.py` - Data migration script

---

*Phase 5 completed as part of Software Reengineering project*
