"""
Inventory Service - Manages item inventory operations.
Replaces legacy Inventory.java with improved patterns.
"""
import logging
from app import db
from app.models.item import Item, ItemType

logger = logging.getLogger(__name__)


class InventoryError(Exception):
    """Custom exception for inventory errors."""
    pass


class InventoryService:
    """
    Inventory service with centralized inventory management.
    
    Improvements over legacy system:
    - Repository pattern for data access
    - Transaction support
    - Better error handling
    - Search and filtering capabilities
    """
    
    @staticmethod
    def get_all_items(item_type=None, active_only=True):
        """
        Get all items, optionally filtered.
        
        Args:
            item_type: Filter by item type (sale/rental)
            active_only: Only return active items
            
        Returns:
            list: List of Item objects
        """
        query = Item.query
        
        if item_type:
            query = query.filter_by(item_type=item_type)
        
        if active_only:
            query = query.filter_by(is_active=True)
        
        return query.order_by(Item.name).all()
    
    @staticmethod
    def get_sale_items(active_only=True):
        """Get all sale items."""
        return InventoryService.get_all_items(ItemType.SALE, active_only)
    
    @staticmethod
    def get_rental_items(active_only=True):
        """Get all rental items."""
        return InventoryService.get_all_items(ItemType.RENTAL, active_only)
    
    @staticmethod
    def get_item_by_id(item_id):
        """
        Get item by item_id.
        
        Args:
            item_id: Item ID string (e.g., 'A001')
            
        Returns:
            Item: Item object or None
        """
        return Item.query.filter_by(item_id=item_id).first()
    
    @staticmethod
    def get_item(id):
        """
        Get item by database ID.
        
        Args:
            id: Database primary key
            
        Returns:
            Item: Item object or None
        """
        return Item.query.get(id)
    
    @staticmethod
    def search_items(query, item_type=None):
        """
        Search items by name.
        
        Args:
            query: Search query string
            item_type: Optional item type filter
            
        Returns:
            list: Matching items
        """
        search = Item.query.filter(
            Item.name.ilike(f'%{query}%')
        )
        
        if item_type:
            search = search.filter_by(item_type=item_type)
        
        return search.filter_by(is_active=True).all()
    
    @staticmethod
    def add_item(item_id, name, price, quantity=0, item_type=ItemType.SALE, description=None):
        """
        Add new item to inventory.
        
        Args:
            item_id: Unique item ID
            name: Item name
            price: Unit price
            quantity: Initial quantity
            item_type: Item type (sale/rental)
            description: Item description
            
        Returns:
            Item: Created item
            
        Raises:
            InventoryError: If item creation fails
        """
        # Check if item_id exists
        existing = Item.query.filter_by(item_id=item_id).first()
        if existing:
            raise InventoryError(f'Item ID {item_id} already exists')
        
        item = Item(
            item_id=item_id,
            name=name,
            price=price,
            quantity=quantity,
            item_type=item_type,
            description=description
        )
        
        db.session.add(item)
        db.session.commit()
        
        logger.info(f'Item added: {item_id} - {name}')
        
        return item
    
    @staticmethod
    def update_item(item, name=None, price=None, quantity=None, description=None):
        """
        Update item details.
        
        Args:
            item: Item model instance
            name: New name (optional)
            price: New price (optional)
            quantity: New quantity (optional)
            description: New description (optional)
            
        Returns:
            Item: Updated item
        """
        if name is not None:
            item.name = name
        if price is not None:
            item.price = price
        if quantity is not None:
            item.quantity = quantity
        if description is not None:
            item.description = description
        
        db.session.commit()
        
        logger.info(f'Item updated: {item.item_id}')
        
        return item
    
    @staticmethod
    def add_stock(item, amount):
        """
        Add stock to an item.
        
        Args:
            item: Item model instance
            amount: Amount to add
            
        Returns:
            Item: Updated item
            
        Raises:
            InventoryError: If amount is invalid
        """
        if amount <= 0:
            raise InventoryError('Amount must be positive')
        
        item.add_stock(amount)
        db.session.commit()
        
        logger.info(f'Stock added: {item.item_id} +{amount} (new total: {item.quantity})')
        
        return item
    
    @staticmethod
    def remove_stock(item, amount):
        """
        Remove stock from an item.
        
        Args:
            item: Item model instance
            amount: Amount to remove
            
        Returns:
            Item: Updated item
            
        Raises:
            InventoryError: If insufficient stock or invalid amount
        """
        if amount <= 0:
            raise InventoryError('Amount must be positive')
        
        if amount > item.quantity:
            raise InventoryError(f'Insufficient stock. Available: {item.quantity}')
        
        item.remove_stock(amount)
        db.session.commit()
        
        logger.info(f'Stock removed: {item.item_id} -{amount} (new total: {item.quantity})')
        
        return item
    
    @staticmethod
    def deactivate_item(item):
        """
        Deactivate an item (soft delete).
        
        Args:
            item: Item model instance
            
        Returns:
            Item: Deactivated item
        """
        item.is_active = False
        db.session.commit()
        
        logger.info(f'Item deactivated: {item.item_id}')
        
        return item
    
    @staticmethod
    def activate_item(item):
        """
        Activate an item.
        
        Args:
            item: Item model instance
            
        Returns:
            Item: Activated item
        """
        item.is_active = True
        db.session.commit()
        
        logger.info(f'Item activated: {item.item_id}')
        
        return item
    
    @staticmethod
    def get_low_stock_items(threshold=None):
        """
        Get items below low stock threshold.
        
        Args:
            threshold: Optional override threshold
            
        Returns:
            list: List of low stock items
        """
        if threshold:
            return Item.query.filter(
                Item.quantity <= threshold,
                Item.is_active == True
            ).all()
        
        return Item.query.filter(
            Item.quantity <= Item.low_stock_threshold,
            Item.is_active == True
        ).all()
    
    @staticmethod
    def get_out_of_stock_items():
        """Get all out of stock items."""
        return Item.query.filter(
            Item.quantity == 0,
            Item.is_active == True
        ).all()
    
    @staticmethod
    def get_inventory_value():
        """Calculate total inventory value."""
        result = db.session.query(
            db.func.sum(Item.price * Item.quantity)
        ).filter(Item.is_active == True).scalar()
        
        return result or 0.0
    
    @staticmethod
    def get_inventory_stats():
        """
        Get inventory statistics.
        
        Returns:
            dict: Inventory statistics
        """
        total_items = Item.query.filter_by(is_active=True).count()
        sale_items = Item.query.filter_by(item_type=ItemType.SALE, is_active=True).count()
        rental_items = Item.query.filter_by(item_type=ItemType.RENTAL, is_active=True).count()
        low_stock = len(InventoryService.get_low_stock_items())
        out_of_stock = len(InventoryService.get_out_of_stock_items())
        total_value = InventoryService.get_inventory_value()
        
        return {
            'total_items': total_items,
            'sale_items': sale_items,
            'rental_items': rental_items,
            'low_stock': low_stock,
            'out_of_stock': out_of_stock,
            'total_value': total_value
        }
