"""
Celery tasks for Cart app.
"""

import logging
from celery import shared_task
from django.utils import timezone
from django.db import transaction
from django.core.cache import cache

from .models import Cart, CartItem
from .services import CartService

logger = logging.getLogger(__name__)


@shared_task(bind=True, name='cart.cleanup_expired_carts')
def cleanup_expired_carts(self):
    """
    Clean up expired carts and cart items.
    This task runs every 10 minutes.
    """
    try:
        logger.info("Starting cleanup of expired carts...")
        
        now = timezone.now()
        
        # Find expired carts
        expired_carts = Cart.objects.filter(
            expires_at__lt=now,
            is_active=True
        )
        
        if not expired_carts.exists():
            logger.info("No expired carts found")
            return {
                'status': 'success',
                'message': 'No expired carts found',
                'carts_cleaned': 0,
                'items_released': 0
            }
        
        logger.info(f"Found {expired_carts.count()} expired carts")
        
        total_carts_cleaned = 0
        total_items_released = 0
        
        # Process each expired cart
        for cart in expired_carts:
            try:
                with transaction.atomic():
                    # Get expired items in this cart
                    expired_items = cart.items.filter(
                        is_reserved=True,
                        reservation_expires_at__lt=now
                    )
                    
                    items_released = 0
                    for item in expired_items:
                        try:
                            # Release reservation
                            item.release_reservation()
                            items_released += 1
                            
                        except Exception as e:
                            logger.error(f"Error releasing reservation for item {item.id}: {str(e)}")
                            continue
                    
                    # Mark cart as inactive
                    cart.is_active = False
                    cart.save()
                    
                    total_carts_cleaned += 1
                    total_items_released += items_released
                    
                    logger.info(f"Cleaned cart {cart.id}: {items_released} items released")
                    
            except Exception as e:
                logger.error(f"Error cleaning cart {cart.id}: {str(e)}")
                continue
        
        # Clear cart cache
        cache.delete('cart_summary')
        
        logger.info(f"Successfully cleaned {total_carts_cleaned} expired carts, released {total_items_released} items")
        
        return {
            'status': 'success',
            'message': f'Cleaned {total_carts_cleaned} expired carts, released {total_items_released} items',
            'carts_cleaned': total_carts_cleaned,
            'items_released': total_items_released
        }
        
    except Exception as e:
        logger.error(f"Error in cleanup_expired_carts: {str(e)}", exc_info=True)
        return {
            'status': 'error',
            'message': f'Error: {str(e)}',
            'carts_cleaned': 0,
            'items_released': 0
        }


@shared_task(bind=True, name='cart.cleanup_expired_reservations')
def cleanup_expired_reservations(self):
    """
    Clean up expired reservations in cart items.
    This task runs every 5 minutes.
    """
    try:
        logger.info("Starting cleanup of expired cart reservations...")
        
        now = timezone.now()
        
        # Find expired reserved cart items
        expired_items = CartItem.objects.filter(
            is_reserved=True,
            reservation_expires_at__lt=now
        ).select_related('cart')
        
        if not expired_items.exists():
            logger.info("No expired cart reservations found")
            return {
                'status': 'success',
                'message': 'No expired cart reservations found',
                'items_released': 0
            }
        
        logger.info(f"Found {expired_items.count()} expired cart reservations")
        
        total_released = 0
        
        # Process each expired item
        for item in expired_items:
            try:
                with transaction.atomic():
                    # Release reservation
                    item.release_reservation()
                    total_released += 1
                    
                    logger.info(f"Released reservation for cart item {item.id}")
                    
            except Exception as e:
                logger.error(f"Error releasing reservation for item {item.id}: {str(e)}")
                continue
        
        # Clear cart cache
        cache.delete('cart_summary')
        
        logger.info(f"Successfully released {total_released} expired cart reservations")
        
        return {
            'status': 'success',
            'message': f'Released {total_released} expired cart reservations',
            'items_released': total_released
        }
        
    except Exception as e:
        logger.error(f"Error in cleanup_expired_reservations: {str(e)}", exc_info=True)
        return {
            'status': 'error',
            'message': f'Error: {str(e)}',
            'items_released': 0
        }


@shared_task(bind=True, name='cart.validate_cart_integrity')
def validate_cart_integrity(self):
    """
    Validate cart integrity and fix any issues.
    This task runs on demand or can be scheduled.
    """
    try:
        logger.info("Starting cart integrity validation...")
        
        issues_found = 0
        issues_fixed = 0
        
        # Check for orphaned cart items
        orphaned_items = CartItem.objects.filter(cart__isnull=True)
        if orphaned_items.exists():
            logger.warning(f"Found {orphaned_items.count()} orphaned cart items")
            orphaned_items.delete()
            issues_found += 1
            issues_fixed += 1
            logger.info("Deleted orphaned cart items")
        
        # Check for invalid cart states
        invalid_carts = Cart.objects.filter(
            is_active=True,
            expires_at__lt=timezone.now()
        )
        if invalid_carts.exists():
            logger.warning(f"Found {invalid_carts.count()} invalid active carts")
            invalid_carts.update(is_active=False)
            issues_found += 1
            issues_fixed += 1
            logger.info("Fixed invalid cart states")
        
        # Check for inconsistent reservation states
        inconsistent_items = CartItem.objects.filter(
            is_reserved=True,
            reservation_expires_at__isnull=True
        )
        if inconsistent_items.exists():
            logger.warning(f"Found {inconsistent_items.count()} inconsistent reservation states")
            inconsistent_items.update(
                is_reserved=False,
                reservation_expires_at=None
            )
            issues_found += 1
            issues_fixed += 1
            logger.info("Fixed inconsistent reservation states")
        
        if issues_found == 0:
            logger.info("No cart integrity issues found")
            return {
                'status': 'success',
                'message': 'No cart integrity issues found',
                'issues_found': 0,
                'issues_fixed': 0
            }
        else:
            logger.info(f"Found and fixed {issues_fixed} cart integrity issues")
            return {
                'status': 'success',
                'message': f'Found and fixed {issues_fixed} cart integrity issues',
                'issues_found': issues_found,
                'issues_fixed': issues_fixed
            }
            
    except Exception as e:
        logger.error(f"Error in validate_cart_integrity: {str(e)}", exc_info=True)
        return {
            'status': 'error',
            'message': f'Error: {str(e)}',
            'issues_found': 0,
            'issues_fixed': 0
        }


@shared_task(bind=True, name='cart.emergency_cart_cleanup')
def emergency_cart_cleanup(self):
    """
    Emergency cleanup task for critical cart issues.
    This task can be triggered manually when needed.
    """
    try:
        logger.warning("Starting EMERGENCY cart cleanup...")
        
        # Run all cleanup tasks
        result1 = cleanup_expired_carts.delay()
        result2 = cleanup_expired_reservations.delay()
        result3 = validate_cart_integrity.delay()
        
        logger.warning("Emergency cart cleanup tasks queued successfully")
        
        return {
            'status': 'success',
            'message': 'Emergency cart cleanup tasks queued',
            'tasks_queued': [
                'cleanup_expired_carts',
                'cleanup_expired_reservations',
                'validate_cart_integrity'
            ]
        }
        
    except Exception as e:
        logger.error(f"Error in emergency_cart_cleanup: {str(e)}", exc_info=True)
        return {
            'status': 'error',
            'message': f'Error: {str(e)}',
            'tasks_queued': []
        }
