"""
Celery tasks for Events app.
"""

import logging
from celery import shared_task
from django.utils import timezone
from django.db import transaction
from django.core.cache import cache
from django.db.models import Q

from .models import Event, EventPerformance, EventSection, SectionTicketType, Seat
from .optimizations import SeatSelectionOptimizer

logger = logging.getLogger(__name__)


@shared_task(bind=True, name='events.cleanup_expired_reservations')
def cleanup_expired_reservations(self):
    """
    Clean up expired reserved seats and release them back to available.
    This task runs every 5 minutes.
    """
    try:
        logger.info("Starting cleanup of expired reservations...")
        
        now = timezone.now()
        
        # Find expired reserved seats
        expired_seats = Seat.objects.filter(
            status='reserved',
            reservation_expires_at__lt=now
        ).select_related('performance', 'performance__event')
        
        if not expired_seats.exists():
            logger.info("No expired reservations found")
            return {
                'status': 'success',
                'message': 'No expired reservations found',
                'seats_released': 0
            }
        
        logger.info(f"Found {expired_seats.count()} expired reserved seats")
        
        # Group by performance for batch processing
        performance_groups = {}
        for seat in expired_seats:
            perf_key = f"{seat.performance.event.slug} - {seat.performance.date}"
            if perf_key not in performance_groups:
                performance_groups[perf_key] = []
            performance_groups[perf_key].append(seat)
        
        total_released = 0
        affected_performances = set()
        affected_sections = set()
        
        # Process each performance separately
        for perf_key, seats in performance_groups.items():
            logger.info(f"Processing {perf_key}: {len(seats)} seats")
            
            with transaction.atomic():
                # Get seat IDs for this performance
                seat_ids = [seat.id for seat in seats]
                
                # Update seats back to available
                updated_count = Seat.objects.filter(
                    id__in=seat_ids,
                    status='reserved',
                    reservation_expires_at__lt=now
                ).update(
                    status='available',
                    reservation_id=None,
                    reservation_expires_at=None
                )
                
                total_released += updated_count
                
                # Collect affected performances and sections
                for seat in seats:
                    affected_performances.add(seat.performance_id)
                    affected_sections.add(seat.section)
                
                logger.info(f"Released {updated_count} seats for {perf_key}")
        
        # Clear capacity cache for affected sections
        if affected_sections:
            for section_name in affected_sections:
                cache.delete(f"section_capacity_{section_name}")
                logger.info(f"Cleared capacity cache for section: {section_name}")
        
        # Clear performance cache
        if affected_performances:
            for perf_id in affected_performances:
                SeatSelectionOptimizer.invalidate_performance_cache(perf_id)
                logger.info(f"Cleared performance cache for: {perf_id}")
        
        logger.info(f"Successfully released {total_released} expired reserved seats")
        
        return {
            'status': 'success',
            'message': f'Released {total_released} expired reserved seats',
            'seats_released': total_released,
            'affected_performances': len(affected_performances),
            'affected_sections': len(affected_sections)
        }
        
    except Exception as e:
        logger.error(f"Error in cleanup_expired_reservations: {str(e)}", exc_info=True)
        return {
            'status': 'error',
            'message': f'Error: {str(e)}',
            'seats_released': 0
        }


@shared_task(bind=True, name='events.update_capacity_cache')
def update_capacity_cache(self):
    """
    Update capacity cache for all sections.
    This task runs every 30 minutes.
    """
    try:
        logger.info("Starting capacity cache update...")
        
        # Get all sections
        sections = EventSection.objects.select_related('performance', 'performance__event').all()
        
        updated_count = 0
        for section in sections:
            try:
                # Clear existing cache
                section.clear_capacity_cache()
                
                # Force recalculation by accessing computed properties
                _ = section.available_capacity
                _ = section.reserved_capacity
                _ = section.sold_capacity
                
                updated_count += 1
                
            except Exception as e:
                logger.error(f"Error updating cache for section {section.name}: {str(e)}")
                continue
        
        logger.info(f"Successfully updated capacity cache for {updated_count} sections")
        
        return {
            'status': 'success',
            'message': f'Updated capacity cache for {updated_count} sections',
            'sections_updated': updated_count
        }
        
    except Exception as e:
        logger.error(f"Error in update_capacity_cache: {str(e)}", exc_info=True)
        return {
            'status': 'error',
            'message': f'Error: {str(e)}',
            'sections_updated': 0
        }


@shared_task(bind=True, name='events.validate_capacity_consistency')
def validate_capacity_consistency(self):
    """
    Validate and fix capacity inconsistencies.
    This task runs on demand or can be scheduled.
    """
    try:
        logger.info("Starting capacity consistency validation...")
        
        inconsistencies = []
        
        # Check all SectionTicketType objects
        for stt in SectionTicketType.objects.select_related('section', 'ticket_type').all():
            try:
                # Get actual seat counts
                actual_available = Seat.objects.filter(
                    performance=stt.section.performance,
                    section=stt.section.name,
                    ticket_type=stt.ticket_type,
                    status='available'
                ).count()
                
                actual_reserved = Seat.objects.filter(
                    performance=stt.section.performance,
                    section=stt.section.name,
                    ticket_type=stt.ticket_type,
                    status='reserved'
                ).count()
                
                actual_sold = Seat.objects.filter(
                    performance=stt.section.performance,
                    section=stt.section.name,
                    ticket_type=stt.ticket_type,
                    status='sold'
                ).count()
                
                # Check if there's a mismatch
                if (stt.available_capacity != actual_available or
                    stt.reserved_capacity != actual_reserved or
                    stt.sold_capacity != actual_sold):
                    
                    inconsistencies.append({
                        'stt': stt,
                        'stored': {
                            'available': stt.available_capacity,
                            'reserved': stt.reserved_capacity,
                            'sold': stt.sold_capacity
                        },
                        'actual': {
                            'available': actual_available,
                            'reserved': actual_reserved,
                            'sold': actual_sold
                        }
                    })
                    
            except Exception as e:
                logger.error(f"Error checking STT {stt.id}: {str(e)}")
                continue
        
        if inconsistencies:
            logger.warning(f"Found {len(inconsistencies)} capacity inconsistencies")
            
            # Fix inconsistencies
            fixed_count = 0
            for inc in inconsistencies:
                try:
                    stt = inc['stt']
                    actual = inc['actual']
                    
                    # Update with actual values
                    stt.available_capacity = actual['available']
                    stt.reserved_capacity = actual['reserved']
                    stt.sold_capacity = actual['sold']
                    stt.save()
                    
                    fixed_count += 1
                    logger.info(f"Fixed capacity for {stt.section.name} - {stt.ticket_type.name}")
                    
                except Exception as e:
                    logger.error(f"Error fixing inconsistency: {str(e)}")
                    continue
            
            logger.info(f"Fixed {fixed_count} capacity inconsistencies")
            
            return {
                'status': 'success',
                'message': f'Fixed {fixed_count} capacity inconsistencies',
                'inconsistencies_found': len(inconsistencies),
                'inconsistencies_fixed': fixed_count
            }
        else:
            logger.info("No capacity inconsistencies found")
            return {
                'status': 'success',
                'message': 'No capacity inconsistencies found',
                'inconsistencies_found': 0,
                'inconsistencies_fixed': 0
            }
            
    except Exception as e:
        logger.error(f"Error in validate_capacity_consistency: {str(e)}", exc_info=True)
        return {
            'status': 'error',
            'message': f'Error: {str(e)}',
            'inconsistencies_found': 0,
            'inconsistencies_fixed': 0
        }


@shared_task(bind=True, name='events.emergency_capacity_cleanup')
def emergency_capacity_cleanup(self):
    """
    Emergency cleanup task for critical capacity issues.
    This task can be triggered manually when needed.
    """
    try:
        logger.warning("Starting EMERGENCY capacity cleanup...")
        
        # Run all cleanup tasks
        result1 = cleanup_expired_reservations.delay()
        result2 = update_capacity_cache.delay()
        result3 = validate_capacity_consistency.delay()
        
        logger.warning("Emergency cleanup tasks queued successfully")
        
        return {
            'status': 'success',
            'message': 'Emergency cleanup tasks queued',
            'tasks_queued': [
                'cleanup_expired_reservations',
                'update_capacity_cache', 
                'validate_capacity_consistency'
            ]
        }
        
    except Exception as e:
        logger.error(f"Error in emergency_capacity_cleanup: {str(e)}", exc_info=True)
        return {
            'status': 'error',
            'message': f'Error: {str(e)}',
            'tasks_queued': []
        }
