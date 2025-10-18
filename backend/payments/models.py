"""
Payment models for Peykan Tourism Platform.
"""

from decimal import Decimal
from django.db import models
from django.utils.translation import gettext_lazy as _
from core.models import BaseModel


class Payment(BaseModel):
    """
    Payment model for tracking transactions.
    """
    
    # Payment identification
    payment_id = models.CharField(
        max_length=50, 
        unique=True,
        verbose_name=_('Payment ID')
    )
    order = models.ForeignKey(
        'orders.Order', 
        on_delete=models.CASCADE, 
        related_name='payments',
        verbose_name=_('Order')
    )
    
    # Payment details
    PAYMENT_METHOD_CHOICES = [
        ('credit_card', _('Credit Card')),
        ('debit_card', _('Debit Card')),
        ('bank_transfer', _('Bank Transfer')),
        ('cash', _('Cash')),
        ('online', _('Online Payment')),
        ('wallet', _('Digital Wallet')),
    ]
    payment_method = models.CharField(
        max_length=20, 
        choices=PAYMENT_METHOD_CHOICES,
        verbose_name=_('Payment method')
    )
    
    # Amount and currency
    amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        verbose_name=_('Amount')
    )
    currency = models.CharField(max_length=3, default='USD', verbose_name=_('Currency'))
    
    # Status
    STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('processing', _('Processing')),
        ('completed', _('Completed')),
        ('failed', _('Failed')),
        ('cancelled', _('Cancelled')),
        ('refunded', _('Refunded')),
    ]
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='pending',
        verbose_name=_('Status')
    )
    
    # Gateway information
    gateway = models.CharField(
        max_length=50, 
        blank=True,
        verbose_name=_('Payment gateway')
    )
    gateway_transaction_id = models.CharField(
        max_length=100, 
        blank=True,
        verbose_name=_('Gateway transaction ID')
    )
    
    # Customer information
    customer_name = models.CharField(max_length=255, verbose_name=_('Customer name'))
    customer_email = models.EmailField(verbose_name=_('Customer email'))
    
    # Additional data
    metadata = models.JSONField(
        default=dict,
        blank=True,
        verbose_name=_('Metadata')
    )
    error_message = models.TextField(blank=True, verbose_name=_('Error message'))
    
    class Meta:
        verbose_name = _('Payment')
        verbose_name_plural = _('Payments')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Payment {self.payment_id} - {self.order.order_number}"
    
    def save(self, *args, **kwargs):
        if not self.payment_id:
            self.payment_id = f"PAY{str(self.id)[:8].upper()}"
        super().save(*args, **kwargs)
    
    @property
    def is_successful(self):
        """Check if payment was successful."""
        return self.status == 'completed'
    
    @property
    def is_failed(self):
        """Check if payment failed."""
        return self.status == 'failed'
    
    @property
    def is_pending(self):
        """Check if payment is pending."""
        return self.status == 'pending'


class PaymentTransaction(BaseModel):
    """
    Payment transaction history.
    """
    
    payment = models.ForeignKey(
        Payment, 
        on_delete=models.CASCADE, 
        related_name='transactions',
        verbose_name=_('Payment')
    )
    
    # Transaction details
    TRANSACTION_TYPE_CHOICES = [
        ('authorization', _('Authorization')),
        ('capture', _('Capture')),
        ('refund', _('Refund')),
        ('void', _('Void')),
        ('chargeback', _('Chargeback')),
    ]
    transaction_type = models.CharField(
        max_length=20, 
        choices=TRANSACTION_TYPE_CHOICES,
        verbose_name=_('Transaction type')
    )
    
    # Amount
    amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        verbose_name=_('Amount')
    )
    currency = models.CharField(max_length=3, default='USD', verbose_name=_('Currency'))
    
    # Status
    STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('success', _('Success')),
        ('failed', _('Failed')),
    ]
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='pending',
        verbose_name=_('Status')
    )
    
    # Gateway response
    gateway_response = models.JSONField(
        default=dict,
        blank=True,
        verbose_name=_('Gateway response')
    )
    error_code = models.CharField(
        max_length=50, 
        blank=True,
        verbose_name=_('Error code')
    )
    error_message = models.TextField(blank=True, verbose_name=_('Error message'))
    
    class Meta:
        verbose_name = _('Payment Transaction')
        verbose_name_plural = _('Payment Transactions')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.payment.payment_id} - {self.transaction_type}"


class PaymentService:
    """
    Service class for payment operations.
    """
    
    @staticmethod
    def create_payment(order, payment_method, amount, gateway='mock'):
        """Create a new payment."""
        payment = Payment.objects.create(
            order=order,
            payment_method=payment_method,
            amount=amount,
            currency=order.currency,
            customer_name=order.customer_name,
            customer_email=order.customer_email,
            gateway=gateway,
        )
        
        return payment
    
    @staticmethod
    def process_payment(payment, payment_data=None):
        """Process payment through gateway."""
        try:
            # Mock payment processing for development
            if payment.gateway == 'mock':
                return PaymentService._process_mock_payment(payment, payment_data)
            
            # Add real payment gateway integration here
            # Example: Stripe, PayPal, etc.
            else:
                return PaymentService._process_real_payment(payment, payment_data)
        
        except Exception as e:
            payment.status = 'failed'
            payment.error_message = str(e)
            payment.save()
            
            # Create failed transaction
            PaymentTransaction.objects.create(
                payment=payment,
                transaction_type='authorization',
                amount=payment.amount,
                currency=payment.currency,
                status='failed',
                error_message=str(e),
            )
            
            return False
    
    @staticmethod
    def _process_mock_payment(payment, payment_data):
        """Process mock payment for development."""
        import random
        
        # Simulate payment processing
        success_rate = 0.9  # 90% success rate
        
        if random.random() < success_rate:
            payment.status = 'completed'
            payment.gateway_transaction_id = f"MOCK_{payment.payment_id}"
            payment.save()
            
            # Create successful transaction
            PaymentTransaction.objects.create(
                payment=payment,
                transaction_type='authorization',
                amount=payment.amount,
                currency=payment.currency,
                status='success',
                gateway_response={'mock': True, 'success': True},
            )
            
            # Update order payment status
            from orders.models import OrderService
            OrderService.update_payment_status(
                payment.order, 
                'paid', 
                payment.payment_method
            )
            
            return True
        else:
            payment.status = 'failed'
            payment.error_message = 'Mock payment failed'
            payment.save()
            
            # Create failed transaction
            PaymentTransaction.objects.create(
                payment=payment,
                transaction_type='authorization',
                amount=payment.amount,
                currency=payment.currency,
                status='failed',
                error_message='Mock payment failed',
            )
            
            return False
    
    @staticmethod
    def _process_real_payment(payment, payment_data):
        """Process real payment through gateway."""
        # Implement real payment gateway integration
        # This is a placeholder for actual implementation
        raise NotImplementedError("Real payment processing not implemented")
    
    @staticmethod
    def refund_payment(payment, amount=None, reason=None):
        """Refund a payment."""
        if not payment.is_successful:
            return False
        
        refund_amount = amount or payment.amount
        
        try:
            # Mock refund processing
            if payment.gateway == 'mock':
                payment.status = 'refunded'
                payment.save()
                
                # Create refund transaction
                PaymentTransaction.objects.create(
                    payment=payment,
                    transaction_type='refund',
                    amount=refund_amount,
                    currency=payment.currency,
                    status='success',
                    gateway_response={'mock': True, 'refund': True},
                )
                
                # Update order payment status
                from orders.models import OrderService
                OrderService.update_payment_status(payment.order, 'refunded')
                
                return True
            
            else:
                # Implement real refund processing
                raise NotImplementedError("Real refund processing not implemented")
        
        except Exception as e:
            # Create failed refund transaction
            PaymentTransaction.objects.create(
                payment=payment,
                transaction_type='refund',
                amount=refund_amount,
                currency=payment.currency,
                status='failed',
                error_message=str(e),
            )
            
            return False
    
    @staticmethod
    def get_payment_summary(payment):
        """Get payment summary."""
        transactions = payment.transactions.all()
        
        summary = {
            'payment_id': payment.payment_id,
            'order_number': payment.order.order_number,
            'payment_method': payment.payment_method,
            'amount': float(payment.amount),
            'currency': payment.currency,
            'status': payment.status,
            'gateway': payment.gateway,
            'customer_name': payment.customer_name,
            'customer_email': payment.customer_email,
            'created_at': payment.created_at.isoformat(),
            'transactions': []
        }
        
        for transaction in transactions:
            summary['transactions'].append({
                'id': str(transaction.id),
                'transaction_type': transaction.transaction_type,
                'amount': float(transaction.amount),
                'status': transaction.status,
                'created_at': transaction.created_at.isoformat(),
            })
        
        return summary 