"""
Transaction Model - Represents sales and purchase transactions.
Replaces legacy POS.java, POR.java transaction handling.
"""
from datetime import datetime
from app import db


class TransactionType:
    """Transaction type constants."""
    SALE = 'sale'
    RENTAL = 'rental'
    RETURN = 'return'
    
    @classmethod
    def all_types(cls):
        return [cls.SALE, cls.RENTAL, cls.RETURN]


class PaymentMethod:
    """Payment method constants."""
    CASH = 'cash'
    CREDIT = 'credit'
    DEBIT = 'debit'
    
    @classmethod
    def all_methods(cls):
        return [cls.CASH, cls.CREDIT, cls.DEBIT]


class Transaction(db.Model):
    """
    Transaction model representing sales/rental/return transactions.
    
    Improvements over legacy system:
    - Complete transaction tracking
    - Payment method recording
    - Coupon discount application
    - Full audit trail
    """
    __tablename__ = 'transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    transaction_number = db.Column(db.String(20), unique=True, nullable=False, index=True)
    transaction_type = db.Column(db.String(20), nullable=False, default=TransactionType.SALE)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=True)
    coupon_id = db.Column(db.Integer, db.ForeignKey('coupons.id'), nullable=True)
    
    # Financial details
    subtotal = db.Column(db.Float, nullable=False, default=0.0)
    discount_amount = db.Column(db.Float, default=0.0)
    tax_amount = db.Column(db.Float, default=0.0)
    total = db.Column(db.Float, nullable=False, default=0.0)
    
    # Payment
    payment_method = db.Column(db.String(20), nullable=False, default=PaymentMethod.CASH)
    amount_tendered = db.Column(db.Float, default=0.0)
    change_given = db.Column(db.Float, default=0.0)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    items = db.relationship('TransactionItem', backref='transaction', lazy='dynamic',
                           cascade='all, delete-orphan')
    rentals = db.relationship('Rental', backref='transaction', lazy='dynamic')
    
    def __init__(self, transaction_number, transaction_type=TransactionType.SALE, 
                 employee_id=None, customer_id=None, payment_method=PaymentMethod.CASH):
        self.transaction_number = transaction_number
        self.transaction_type = transaction_type
        self.employee_id = employee_id
        self.customer_id = customer_id
        self.payment_method = payment_method
    
    def calculate_totals(self, tax_rate=0.08):
        """
        Calculate transaction totals.
        
        Args:
            tax_rate: Tax rate as decimal (default 8%)
        """
        # Calculate subtotal from items
        self.subtotal = sum(
            item.quantity * item.unit_price 
            for item in self.items.all()
        )
        
        # Apply coupon discount if any
        if self.coupon_id:
            from app.models.coupon import Coupon
            coupon = Coupon.query.get(self.coupon_id)
            if coupon and coupon.is_valid():
                self.discount_amount = self.subtotal * (coupon.discount_percent / 100)
        
        # Calculate tax on discounted amount
        taxable_amount = self.subtotal - self.discount_amount
        self.tax_amount = taxable_amount * tax_rate
        
        # Calculate total
        self.total = taxable_amount + self.tax_amount
    
    def apply_payment(self, amount_tendered):
        """
        Apply payment and calculate change.
        
        Args:
            amount_tendered: Amount given by customer
        """
        self.amount_tendered = amount_tendered
        if self.payment_method == PaymentMethod.CASH:
            self.change_given = max(0, amount_tendered - self.total)
    
    def add_item(self, item, quantity, unit_price=None):
        """
        Add item to transaction.
        
        Args:
            item: Item model instance
            quantity: Quantity to add
            unit_price: Override price (optional)
        """
        price = unit_price or item.price
        trans_item = TransactionItem(
            transaction_id=self.id,
            item_id=item.id,
            quantity=quantity,
            unit_price=price
        )
        db.session.add(trans_item)
    
    def is_sale(self):
        """Check if transaction is a sale."""
        return self.transaction_type == TransactionType.SALE
    
    def is_rental(self):
        """Check if transaction is a rental."""
        return self.transaction_type == TransactionType.RENTAL
    
    def is_return(self):
        """Check if transaction is a return."""
        return self.transaction_type == TransactionType.RETURN
    
    def to_dict(self):
        """Convert to dictionary for API responses."""
        return {
            'id': self.id,
            'transaction_number': self.transaction_number,
            'transaction_type': self.transaction_type,
            'employee_id': self.employee_id,
            'customer_id': self.customer_id,
            'subtotal': self.subtotal,
            'discount_amount': self.discount_amount,
            'tax_amount': self.tax_amount,
            'total': self.total,
            'payment_method': self.payment_method,
            'amount_tendered': self.amount_tendered,
            'change_given': self.change_given,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'items': [item.to_dict() for item in self.items.all()]
        }
    
    @staticmethod
    def generate_transaction_number():
        """Generate unique transaction number."""
        from datetime import datetime
        import random
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        random_suffix = random.randint(100, 999)
        return f'TXN{timestamp}{random_suffix}'
    
    def __repr__(self):
        return f'<Transaction {self.transaction_number}: ${self.total:.2f}>'


class TransactionItem(db.Model):
    """
    Transaction item model - line items within a transaction.
    """
    __tablename__ = 'transaction_items'
    
    id = db.Column(db.Integer, primary_key=True)
    transaction_id = db.Column(db.Integer, db.ForeignKey('transactions.id'), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('items.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    unit_price = db.Column(db.Float, nullable=False)
    
    def __init__(self, transaction_id, item_id, quantity, unit_price):
        self.transaction_id = transaction_id
        self.item_id = item_id
        self.quantity = quantity
        self.unit_price = unit_price
    
    @property
    def line_total(self):
        """Calculate line total."""
        return self.quantity * self.unit_price
    
    def to_dict(self):
        """Convert to dictionary for API responses."""
        return {
            'id': self.id,
            'transaction_id': self.transaction_id,
            'item_id': self.item_id,
            'item_name': self.item.name if self.item else None,
            'quantity': self.quantity,
            'unit_price': self.unit_price,
            'line_total': self.line_total
        }
    
    def __repr__(self):
        return f'<TransactionItem {self.item_id} x{self.quantity}>'
