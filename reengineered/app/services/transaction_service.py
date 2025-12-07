"""
Transaction Service - Handles sale, rental, and return transactions.
Replaces legacy POS.java, POR.java, POH.java with unified service.
"""
import logging
from datetime import datetime
from app import db
from app.models.item import Item, ItemType
from app.models.customer import Customer
from app.models.transaction import Transaction, TransactionItem, TransactionType, PaymentMethod
from app.models.rental import Rental
from app.services.inventory_service import InventoryService

logger = logging.getLogger(__name__)


class TransactionError(Exception):
    """Custom exception for transaction errors."""
    pass


class TransactionService:
    """
    Transaction service for processing sales, rentals, and returns.
    
    Improvements over legacy system:
    - Unified transaction handling
    - Proper transaction rollback
    - Complete audit trail
    - Tax calculation
    """
    
    @staticmethod
    def create_sale(employee_id, items, payment_method=PaymentMethod.CASH, 
                   amount_tendered=0, coupon_code=None, customer_phone=None):
        """
        Process a sale transaction.
        
        Args:
            employee_id: ID of employee processing sale
            items: List of dicts with item_id and quantity
            payment_method: Payment method
            amount_tendered: Amount given by customer
            coupon_code: Optional coupon code
            customer_phone: Optional customer phone
            
        Returns:
            Transaction: Completed transaction
            
        Raises:
            TransactionError: If transaction fails
        """
        try:
            # Get or create customer if phone provided
            customer = None
            if customer_phone:
                customer = Customer.query.filter_by(phone=customer_phone).first()
                if not customer:
                    customer = Customer(phone=customer_phone)
                    db.session.add(customer)
            
            # Create transaction
            transaction = Transaction(
                transaction_number=Transaction.generate_transaction_number(),
                transaction_type=TransactionType.SALE,
                employee_id=employee_id,
                customer_id=customer.id if customer else None,
                payment_method=payment_method
            )
            db.session.add(transaction)
            db.session.flush()  # Get transaction ID
            
            # Process items
            for item_data in items:
                item = InventoryService.get_item_by_id(item_data['item_id'])
                if not item:
                    raise TransactionError(f"Item {item_data['item_id']} not found")
                
                quantity = item_data['quantity']
                
                # Check stock
                if item.quantity < quantity:
                    raise TransactionError(
                        f"Insufficient stock for {item.name}. Available: {item.quantity}"
                    )
                
                # Add to transaction
                trans_item = TransactionItem(
                    transaction_id=transaction.id,
                    item_id=item.id,
                    quantity=quantity,
                    unit_price=item.price
                )
                db.session.add(trans_item)
                
                # Update inventory
                item.remove_stock(quantity)
            
            # Apply coupon if provided
            if coupon_code:
                from app.services.coupon_service import CouponService
                coupon = CouponService.get_coupon_by_code(coupon_code)
                if coupon and coupon.is_valid():
                    transaction.coupon_id = coupon.id
                    coupon.use()
            
            # Calculate totals
            transaction.calculate_totals()
            
            # Apply payment
            transaction.apply_payment(amount_tendered)
            
            db.session.commit()
            
            logger.info(f'Sale completed: {transaction.transaction_number} - ${transaction.total:.2f}')
            
            return transaction
            
        except Exception as e:
            db.session.rollback()
            logger.error(f'Sale failed: {str(e)}')
            raise TransactionError(str(e))
    
    @staticmethod
    def create_rental(employee_id, customer_phone, items, rental_days=7,
                     payment_method=PaymentMethod.CASH, amount_tendered=0):
        """
        Process a rental transaction.
        
        Args:
            employee_id: ID of employee processing rental
            customer_phone: Customer phone number (required)
            items: List of dicts with item_id and quantity
            rental_days: Number of days for rental
            payment_method: Payment method
            amount_tendered: Amount given by customer
            
        Returns:
            Transaction: Completed transaction
            
        Raises:
            TransactionError: If transaction fails
        """
        if not customer_phone:
            raise TransactionError("Customer phone is required for rentals")
        
        try:
            # Get or create customer
            customer = Customer.query.filter_by(phone=customer_phone).first()
            if not customer:
                customer = Customer(phone=customer_phone)
                db.session.add(customer)
                db.session.flush()
            
            # Create transaction
            transaction = Transaction(
                transaction_number=Transaction.generate_transaction_number(),
                transaction_type=TransactionType.RENTAL,
                employee_id=employee_id,
                customer_id=customer.id,
                payment_method=payment_method
            )
            db.session.add(transaction)
            db.session.flush()
            
            # Process rental items
            for item_data in items:
                item = InventoryService.get_item_by_id(item_data['item_id'])
                if not item:
                    raise TransactionError(f"Item {item_data['item_id']} not found")
                
                if item.item_type != ItemType.RENTAL:
                    raise TransactionError(f"{item.name} is not available for rental")
                
                quantity = item_data['quantity']
                
                # Check stock
                if item.quantity < quantity:
                    raise TransactionError(
                        f"Insufficient stock for {item.name}. Available: {item.quantity}"
                    )
                
                # Add to transaction
                trans_item = TransactionItem(
                    transaction_id=transaction.id,
                    item_id=item.id,
                    quantity=quantity,
                    unit_price=item.price
                )
                db.session.add(trans_item)
                
                # Create rental record
                rental = Rental(
                    customer_id=customer.id,
                    item_id=item.id,
                    rental_price=item.price,
                    quantity=quantity,
                    rental_days=rental_days,
                    transaction_id=transaction.id
                )
                db.session.add(rental)
                
                # Update inventory
                item.remove_stock(quantity)
            
            # Calculate totals
            transaction.calculate_totals()
            transaction.apply_payment(amount_tendered)
            
            db.session.commit()
            
            logger.info(f'Rental completed: {transaction.transaction_number}')
            
            return transaction
            
        except Exception as e:
            db.session.rollback()
            logger.error(f'Rental failed: {str(e)}')
            raise TransactionError(str(e))
    
    @staticmethod
    def process_return(employee_id, customer_phone, item_id, quantity=1):
        """
        Process a rental return.
        
        Args:
            employee_id: ID of employee processing return
            customer_phone: Customer phone number
            item_id: Item being returned
            quantity: Quantity being returned
            
        Returns:
            dict: Return details including late fee
            
        Raises:
            TransactionError: If return fails
        """
        try:
            # Find customer
            customer = Customer.query.filter_by(phone=customer_phone).first()
            if not customer:
                raise TransactionError("Customer not found")
            
            # Find item
            item = InventoryService.get_item_by_id(item_id)
            if not item:
                raise TransactionError("Item not found")
            
            # Find active rental
            rental = Rental.query.filter_by(
                customer_id=customer.id,
                item_id=item.id,
                returned=False
            ).first()
            
            if not rental:
                raise TransactionError("No active rental found for this item")
            
            # Process return
            late_fee = rental.process_return()
            
            # Create return transaction if there's a late fee
            transaction = None
            if late_fee > 0:
                transaction = Transaction(
                    transaction_number=Transaction.generate_transaction_number(),
                    transaction_type=TransactionType.RETURN,
                    employee_id=employee_id,
                    customer_id=customer.id,
                    payment_method=PaymentMethod.CASH
                )
                transaction.total = late_fee
                transaction.subtotal = late_fee
                db.session.add(transaction)
            
            db.session.commit()
            
            logger.info(f'Return processed: {item.name} - Late fee: ${late_fee:.2f}')
            
            return {
                'rental': rental,
                'late_fee': late_fee,
                'transaction': transaction,
                'item': item
            }
            
        except Exception as e:
            db.session.rollback()
            logger.error(f'Return failed: {str(e)}')
            raise TransactionError(str(e))
    
    @staticmethod
    def get_transaction(transaction_number):
        """Get transaction by number."""
        return Transaction.query.filter_by(transaction_number=transaction_number).first()
    
    @staticmethod
    def get_transactions(transaction_type=None, employee_id=None, 
                        start_date=None, end_date=None, limit=100):
        """
        Get transactions with optional filters.
        
        Args:
            transaction_type: Filter by type
            employee_id: Filter by employee
            start_date: Filter from date
            end_date: Filter to date
            limit: Maximum results
            
        Returns:
            list: List of transactions
        """
        query = Transaction.query
        
        if transaction_type:
            query = query.filter_by(transaction_type=transaction_type)
        
        if employee_id:
            query = query.filter_by(employee_id=employee_id)
        
        if start_date:
            query = query.filter(Transaction.created_at >= start_date)
        
        if end_date:
            query = query.filter(Transaction.created_at <= end_date)
        
        return query.order_by(Transaction.created_at.desc()).limit(limit).all()
    
    @staticmethod
    def get_daily_sales(date=None):
        """
        Get sales statistics for a day.
        
        Args:
            date: Date to get stats for (default: today)
            
        Returns:
            dict: Sales statistics
        """
        if date is None:
            date = datetime.utcnow().date()
        
        start = datetime.combine(date, datetime.min.time())
        end = datetime.combine(date, datetime.max.time())
        
        transactions = Transaction.query.filter(
            Transaction.created_at >= start,
            Transaction.created_at <= end
        ).all()
        
        total_sales = sum(t.total for t in transactions if t.is_sale())
        total_rentals = sum(t.total for t in transactions if t.is_rental())
        total_returns = sum(t.total for t in transactions if t.is_return())
        
        return {
            'date': date.isoformat(),
            'transaction_count': len(transactions),
            'total_sales': total_sales,
            'total_rentals': total_rentals,
            'total_returns': total_returns,
            'grand_total': total_sales + total_rentals + total_returns
        }
