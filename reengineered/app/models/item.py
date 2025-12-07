"""
Item Model - Represents products in the POS system.
Replaces legacy Item.java and item database management.
"""
from datetime import datetime
from app import db


class ItemType:
    """Item type constants."""
    SALE = 'sale'
    RENTAL = 'rental'
    
    @classmethod
    def all_types(cls):
        return [cls.SALE, cls.RENTAL]


class Item(db.Model):
    """
    Item model representing products in inventory.
    
    Improvements over legacy system:
    - Proper data types with validation
    - Item type differentiation (sale vs rental)
    - Soft delete support
    - Full audit trail
    """
    __tablename__ = 'items'
    
    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.String(10), unique=True, nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False, index=True)
    price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=0)
    item_type = db.Column(db.String(20), nullable=False, default=ItemType.SALE)
    description = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    low_stock_threshold = db.Column(db.Integer, default=10)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    transaction_items = db.relationship('TransactionItem', backref='item', lazy='dynamic')
    rentals = db.relationship('Rental', backref='item', lazy='dynamic')
    
    def __init__(self, item_id, name, price, quantity=0, item_type=ItemType.SALE, description=None):
        self.item_id = item_id
        self.name = name
        self.price = price
        self.quantity = quantity
        self.item_type = item_type
        self.description = description
    
    def is_in_stock(self):
        """Check if item is in stock."""
        return self.quantity > 0
    
    def is_low_stock(self):
        """Check if item is below low stock threshold."""
        return self.quantity <= self.low_stock_threshold
    
    def add_stock(self, amount):
        """
        Add stock to item.
        
        Args:
            amount: Number of items to add
        """
        if amount < 0:
            raise ValueError("Amount cannot be negative")
        self.quantity += amount
    
    def remove_stock(self, amount):
        """
        Remove stock from item.
        
        Args:
            amount: Number of items to remove
            
        Returns:
            bool: True if successful
            
        Raises:
            ValueError: If insufficient stock
        """
        if amount < 0:
            raise ValueError("Amount cannot be negative")
        if amount > self.quantity:
            raise ValueError(f"Insufficient stock. Available: {self.quantity}")
        self.quantity -= amount
        return True
    
    def is_rental_item(self):
        """Check if item is a rental item."""
        return self.item_type == ItemType.RENTAL
    
    def is_sale_item(self):
        """Check if item is a sale item."""
        return self.item_type == ItemType.SALE
    
    def calculate_total(self, qty):
        """
        Calculate total price for quantity.
        
        Args:
            qty: Quantity to calculate for
            
        Returns:
            float: Total price
        """
        return self.price * qty
    
    def to_dict(self):
        """Convert to dictionary for API responses."""
        return {
            'id': self.id,
            'item_id': self.item_id,
            'name': self.name,
            'price': self.price,
            'quantity': self.quantity,
            'item_type': self.item_type,
            'description': self.description,
            'is_active': self.is_active,
            'is_in_stock': self.is_in_stock(),
            'is_low_stock': self.is_low_stock(),
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<Item {self.item_id}: {self.name} (${self.price:.2f})>'
