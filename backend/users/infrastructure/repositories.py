"""
Infrastructure Layer - Repository Implementations
Concrete implementations using Django ORM
"""

from typing import Optional, List
from datetime import datetime, timedelta
import uuid
import random
import string

from django.contrib.auth.hashers import make_password, check_password
from django.utils import timezone
from django.db import transaction

from ..domain.repositories import (
    UserRepository, OTPRepository, UserProfileRepository, UserSessionRepository
)
from ..domain.entities import User, OTPCode, UserProfile, UserSession, UserRole, OTPType
from ..domain.value_objects import Email, PhoneNumber, Password
from ..models import User as UserModel, OTPCode as OTPCodeModel, UserProfile as UserProfileModel, UserSession as UserSessionModel


class DjangoUserRepository(UserRepository):
    """Django ORM implementation of UserRepository"""
    
    def create(self, user: User) -> User:
        """Create a new user"""
        try:
            with transaction.atomic():
                django_user = UserModel.objects.create(
                    id=user.id,
                    username=user.username,
                    email=user.email,
                    first_name=user.first_name,
                    last_name=user.last_name,
                    phone_number=user.phone_number or '',  # Handle None values
                    date_of_birth=user.date_of_birth,
                    nationality=user.nationality or '',  # Handle None values
                    preferred_language=user.preferred_language,
                    preferred_currency=user.preferred_currency,
                    role=user.role.value,
                    is_active=user.is_active,
                    is_phone_verified=user.is_phone_verified,
                    is_email_verified=user.is_email_verified,
                    commission_rate=user.commission_rate,
                )
                
                # Set password if provided
                if user.password:
                    django_user.set_password(user.password)
                    django_user.save()
                elif user.password_hash:
                    django_user.password = user.password_hash
                    django_user.save()
                
                # Set agent_code separately if provided (since it's unique)
                if user.agent_code:
                    django_user.agent_code = user.agent_code
                    django_user.save()
                
                # Create user profile
                from ..models import UserProfile
                UserProfile.objects.create(user=django_user)
                
                return self._to_domain_entity(django_user)
                
        except Exception as e:
            raise Exception(f"Failed to create user: {e}")
    
    def get_by_id(self, user_id: uuid.UUID) -> Optional[User]:
        """Get user by ID"""
        try:
            django_user = UserModel.objects.get(id=user_id)
            return self._to_domain_entity(django_user)
        except UserModel.DoesNotExist:
            return None
    
    def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        try:
            django_user = UserModel.objects.get(email=email)
            return self._to_domain_entity(django_user)
        except UserModel.DoesNotExist:
            return None
    
    def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        try:
            django_user = UserModel.objects.get(username=username)
            return self._to_domain_entity(django_user)
        except UserModel.DoesNotExist:
            return None
    
    def get_by_phone(self, phone: str) -> Optional[User]:
        """Get user by phone number"""
        try:
            django_user = UserModel.objects.get(phone_number=phone)
            return self._to_domain_entity(django_user)
        except UserModel.DoesNotExist:
            return None
    
    def update(self, user: User) -> User:
        """Update user"""
        try:
            with transaction.atomic():
                django_user = UserModel.objects.get(id=user.id)
                
                # Update fields
                django_user.username = user.username
                django_user.email = user.email
                django_user.first_name = user.first_name
                django_user.last_name = user.last_name
                django_user.phone_number = user.phone_number
                django_user.date_of_birth = user.date_of_birth
                django_user.nationality = user.nationality
                django_user.preferred_language = user.preferred_language
                django_user.preferred_currency = user.preferred_currency
                django_user.role = user.role.value
                django_user.is_active = user.is_active
                django_user.is_phone_verified = user.is_phone_verified
                django_user.is_email_verified = user.is_email_verified
                django_user.commission_rate = user.commission_rate
                
                # Update password if provided
                if user.password:
                    django_user.set_password(user.password)
                elif user.password_hash:
                    django_user.password = user.password_hash
                
                django_user.save()
                
                return self._to_domain_entity(django_user)
                
        except UserModel.DoesNotExist:
            raise Exception(f"User with id {user.id} not found")
        except Exception as e:
            raise Exception(f"Failed to update user: {e}")
    
    def delete(self, user_id: uuid.UUID) -> bool:
        """Delete user"""
        try:
            django_user = UserModel.objects.get(id=user_id)
            django_user.delete()
            return True
        except UserModel.DoesNotExist:
            return False
        except Exception as e:
            raise Exception(f"Failed to delete user: {e}")
    
    def verify_password(self, user_id: uuid.UUID, password: str) -> bool:
        """Verify user password"""
        try:
            django_user = UserModel.objects.get(id=user_id)
            return django_user.check_password(password)
        except UserModel.DoesNotExist:
            return False
    
    def change_password(self, user_id: uuid.UUID, new_password: str) -> bool:
        """Change user password"""
        try:
            django_user = UserModel.objects.get(id=user_id)
            django_user.set_password(new_password)
            django_user.save()
            return True
        except UserModel.DoesNotExist:
            return False
        except Exception as e:
            raise Exception(f"Failed to change password: {e}")
    
    def verify_email(self, user_id: uuid.UUID) -> bool:
        """Mark user email as verified"""
        try:
            django_user = UserModel.objects.get(id=user_id)
            django_user.verify_email()
            return True
        except UserModel.DoesNotExist:
            return False
        except Exception as e:
            raise Exception(f"Failed to verify email: {e}")
    
    def verify_phone(self, user_id: uuid.UUID) -> bool:
        """Mark user phone as verified"""
        try:
            django_user = UserModel.objects.get(id=user_id)
            django_user.verify_phone()
            return True
        except UserModel.DoesNotExist:
            return False
        except Exception as e:
            raise Exception(f"Failed to verify phone: {e}")
    
    def exists_by_username(self, username: str) -> bool:
        """Check if username exists"""
        return UserModel.objects.filter(username=username).exists()
    
    def exists_by_email(self, email: str) -> bool:
        """Check if email exists"""
        return UserModel.objects.filter(email=email).exists()
    
    def exists_by_phone(self, phone: str) -> bool:
        """Check if phone exists"""
        return UserModel.objects.filter(phone_number=phone).exists()
    
    def _to_domain_entity(self, django_user: UserModel) -> User:
        """Convert Django model to domain entity"""
        return User(
            id=django_user.id,
            username=django_user.username,
            email=django_user.email,
            first_name=django_user.first_name,
            last_name=django_user.last_name,
            phone_number=django_user.phone_number,
            date_of_birth=django_user.date_of_birth,
            nationality=django_user.nationality,
            preferred_language=django_user.preferred_language,
            preferred_currency=django_user.preferred_currency,
            role=UserRole(django_user.role),
            is_active=django_user.is_active,
            is_phone_verified=django_user.is_phone_verified,
            is_email_verified=django_user.is_email_verified,
            agent_code=django_user.agent_code,
            commission_rate=django_user.commission_rate,
            created_at=django_user.created_at,
            updated_at=django_user.updated_at,
            password_hash=django_user.password
        )


class DjangoOTPCodeRepository(OTPRepository):
    """Django ORM implementation of OTPRepository for OTPCode"""
    
    def create(self, otp: OTPCode) -> OTPCode:
        """Create a new OTPCode"""
        try:
            django_otp = OTPCodeModel.objects.create(
                id=otp.id,
                user_id=otp.user_id,
                email=otp.email,
                phone=otp.phone,
                otp_type=otp.otp_type.value,
                code=otp.code,
                is_used=otp.is_used,
                expires_at=otp.expires_at,
                used_at=otp.used_at,
            )
            return self._to_domain_entity(django_otp)
        except Exception as e:
            raise Exception(f"Failed to create OTPCode: {e}")
    
    def get_by_id(self, otp_id: uuid.UUID) -> Optional[OTPCode]:
        """Get OTPCode by ID"""
        try:
            django_otp = OTPCodeModel.objects.get(id=otp_id)
            return self._to_domain_entity(django_otp)
        except OTPCodeModel.DoesNotExist:
            return None
    
    def get_valid_otp(self, target: str, otp_type: str, code: str) -> Optional[OTPCode]:
        """Get valid OTPCode by target, type and code"""
        try:
            # Determine if target is email or phone
            is_email = '@' in target
            
            query = {
                'otp_type': otp_type,
                'code': code,
                'is_used': False,
                'expires_at__gt': timezone.now(),
            }
            
            if is_email:
                query['email'] = target
            else:
                query['phone'] = target
            
            django_otp = OTPCodeModel.objects.filter(**query).order_by('-created_at').first()
            
            if django_otp:
                return self._to_domain_entity(django_otp)
            return None
            
        except Exception as e:
            raise Exception(f"Failed to get valid OTPCode: {e}")
    
    def get_latest_otp(self, user_id: uuid.UUID, otp_type: OTPType, email: str = None, phone: str = None) -> Optional[OTPCode]:
        """Get latest OTPCode for user and type"""
        try:
            query = {
                'user_id': user_id,
                'otp_type': otp_type.value,
            }
            
            if email:
                query['email'] = email
            if phone:
                query['phone'] = phone
            
            django_otp = OTPCodeModel.objects.filter(**query).order_by('-created_at').first()
            
            if django_otp:
                return self._to_domain_entity(django_otp)
            return None
            
        except Exception as e:
            raise Exception(f"Failed to get latest OTPCode: {e}")
    
    def mark_as_used(self, otp_id: uuid.UUID) -> bool:
        """Mark OTPCode as used"""
        try:
            django_otp = OTPCodeModel.objects.get(id=otp_id)
            django_otp.mark_as_used()
            return True
        except OTPCodeModel.DoesNotExist:
            return False
        except Exception as e:
            raise Exception(f"Failed to mark OTPCode as used: {e}")
    
    def invalidate_user_otps(self, user_id: uuid.UUID, otp_type: OTPType, email: str = None, phone: str = None) -> bool:
        """Invalidate all OTPCodes for user and type"""
        try:
            query = {
                'user_id': user_id,
                'otp_type': otp_type.value,
                'is_used': False,
            }
            
            if email:
                query['email'] = email
            if phone:
                query['phone'] = phone
            
            OTPCodeModel.objects.filter(**query).update(is_used=True, used_at=timezone.now())
            return True
            
        except Exception as e:
            raise Exception(f"Failed to invalidate OTPCode: {e}")
    
    def cleanup_expired_otps(self) -> int:
        """Clean up expired OTPCodes and return count of deleted OTPCodes"""
        try:
            count, _ = OTPCodeModel.objects.filter(expires_at__lt=timezone.now()).delete()
            return count
        except Exception as e:
            raise Exception(f"Failed to cleanup expired OTPCode: {e}")
    
    def delete(self, otp_id: uuid.UUID) -> bool:
        """Delete OTPCode"""
        try:
            django_otp = OTPCodeModel.objects.get(id=otp_id)
            django_otp.delete()
            return True
        except OTPCodeModel.DoesNotExist:
            return False
        except Exception as e:
            raise Exception(f"Failed to delete OTPCode: {e}")
    
    def delete_expired_otps(self) -> int:
        """Delete expired OTPCodes and return count"""
        try:
            count, _ = OTPCodeModel.objects.filter(expires_at__lt=timezone.now()).delete()
            return count
        except Exception as e:
            raise Exception(f"Failed to delete expired OTPCodes: {e}")
    
    def get_user_otps(self, user_id: uuid.UUID, otp_type: str = None) -> List[OTPCode]:
        """Get all OTPCodes for a user"""
        try:
            query = {'user_id': user_id}
            if otp_type:
                query['otp_type'] = otp_type
            
            django_otps = OTPCodeModel.objects.filter(**query).order_by('-created_at')
            return [self._to_domain_entity(otp) for otp in django_otps]
        except Exception as e:
            raise Exception(f"Failed to get user OTPCodes: {e}")
    
    def mark_as_expired(self, otp_id: uuid.UUID) -> bool:
        """Mark OTPCode as expired"""
        try:
            django_otp = OTPCodeModel.objects.get(id=otp_id)
            django_otp.is_used = True
            django_otp.save()
            return True
        except OTPCodeModel.DoesNotExist:
            return False
        except Exception as e:
            raise Exception(f"Failed to mark OTPCode as expired: {e}")
    
    def update(self, otp: OTPCode) -> OTPCode:
        """Update OTPCode"""
        try:
            django_otp = OTPCodeModel.objects.get(id=otp.id)
            django_otp.is_used = otp.is_used
            django_otp.expires_at = otp.expires_at
            django_otp.save()
            return self._to_domain_entity(django_otp)
        except OTPCodeModel.DoesNotExist:
            raise Exception(f"OTPCode with id {otp.id} not found")
        except Exception as e:
            raise Exception(f"Failed to update OTPCode: {e}")
    
    def generate_otp_code(self) -> str:
        """Generate a random 6-digit OTPCode code"""
        return ''.join(random.choices(string.digits, k=6))
    
    def _to_domain_entity(self, django_otp: OTPCodeModel) -> OTPCode:
        """Convert Django model to domain entity"""
        return OTPCode(
            id=django_otp.id,
            user_id=django_otp.user_id,
            email=django_otp.email,
            phone=django_otp.phone,
            otp_type=OTPType(django_otp.otp_type),
            code=django_otp.code,
            is_used=django_otp.is_used,
            expires_at=django_otp.expires_at,
            created_at=django_otp.created_at,
            used_at=django_otp.used_at,
        )


class DjangoUserProfileRepository(UserProfileRepository):
    """Django ORM implementation of UserProfileRepository"""
    
    def create(self, profile: UserProfile) -> UserProfile:
        """Create a new user profile"""
        profile_model = UserProfileModel.objects.create(
            id=profile.id,
            user_id=profile.user_id,
            avatar=profile.avatar,
            bio=profile.bio or '',  # Handle None values
            address=profile.address or '',  # Handle None values
            city=profile.city or '',  # Handle None values
            country=profile.country or '',  # Handle None values
            postal_code=profile.postal_code or '',  # Handle None values
            website=profile.website or '',  # Handle None values
            facebook=profile.facebook or '',  # Handle None values
            instagram=profile.instagram or '',  # Handle None values
            twitter=profile.twitter or '',  # Handle None values
            newsletter_subscription=profile.newsletter_subscription,
            marketing_emails=profile.marketing_emails,
            created_at=profile.created_at,
            updated_at=profile.updated_at
        )
        
        return self._to_domain_entity(profile_model)
    
    def get_by_user_id(self, user_id: uuid.UUID) -> Optional[UserProfile]:
        """Get profile by user ID"""
        try:
            profile_model = UserProfileModel.objects.get(user_id=user_id)
            return self._to_domain_entity(profile_model)
        except UserProfileModel.DoesNotExist:
            return None
    
    def update(self, profile: UserProfile) -> UserProfile:
        """Update user profile"""
        try:
            profile_model = UserProfileModel.objects.get(user_id=profile.user_id)
            profile_model.avatar = profile.avatar
            profile_model.bio = profile.bio
            profile_model.address = profile.address
            profile_model.city = profile.city
            profile_model.country = profile.country
            profile_model.postal_code = profile.postal_code
            profile_model.website = profile.website
            profile_model.facebook = profile.facebook
            profile_model.instagram = profile.instagram
            profile_model.twitter = profile.twitter
            profile_model.newsletter_subscription = profile.newsletter_subscription
            profile_model.marketing_emails = profile.marketing_emails
            profile_model.updated_at = timezone.now()
            profile_model.save()
            
            return self._to_domain_entity(profile_model)
        except UserProfileModel.DoesNotExist:
            raise ValueError(f"Profile for user {profile.user_id} does not exist")
    
    def delete(self, user_id: uuid.UUID) -> bool:
        """Delete user profile"""
        try:
            profile_model = UserProfileModel.objects.get(user_id=user_id)
            profile_model.delete()
            return True
        except UserProfileModel.DoesNotExist:
            return False
    
    def _to_domain_entity(self, profile_model: UserProfileModel) -> UserProfile:
        """Convert Django model to domain entity"""
        return UserProfile(
            id=profile_model.id,
            user_id=profile_model.user_id,
            avatar=profile_model.avatar,
            bio=profile_model.bio,
            address=profile_model.address,
            city=profile_model.city,
            country=profile_model.country,
            postal_code=profile_model.postal_code,
            website=profile_model.website,
            facebook=profile_model.facebook,
            instagram=profile_model.instagram,
            twitter=profile_model.twitter,
            newsletter_subscription=profile_model.newsletter_subscription,
            marketing_emails=profile_model.marketing_emails,
            created_at=profile_model.created_at,
            updated_at=profile_model.updated_at
        )


class DjangoUserSessionRepository(UserSessionRepository):
    """Django ORM implementation of UserSessionRepository"""
    
    def create(self, session: UserSession) -> UserSession:
        """Create a new user session"""
        session_model = UserSessionModel.objects.create(
            id=session.id,
            user_id=session.user_id,
            session_key=session.session_key,
            ip_address=session.ip_address,
            user_agent=session.user_agent,
            country=session.country or '',  # Handle None values
            city=session.city or '',  # Handle None values
            last_activity=session.last_activity,
            is_active=session.is_active,
            created_at=session.created_at
        )
        
        return self._to_domain_entity(session_model)
    
    def get_by_id(self, session_id: uuid.UUID) -> Optional[UserSession]:
        """Get session by ID"""
        try:
            session_model = UserSessionModel.objects.get(id=session_id)
            return self._to_domain_entity(session_model)
        except UserSessionModel.DoesNotExist:
            return None
    
    def get_by_session_key(self, session_key: str) -> Optional[UserSession]:
        """Get session by session key"""
        try:
            session_model = UserSessionModel.objects.get(session_key=session_key)
            return self._to_domain_entity(session_model)
        except UserSessionModel.DoesNotExist:
            return None
    
    def get_user_sessions(self, user_id: uuid.UUID, active_only: bool = True) -> List[UserSession]:
        """Get all sessions for a user"""
        queryset = UserSessionModel.objects.filter(user_id=user_id)
        if active_only:
            queryset = queryset.filter(is_active=True)
        
        return [self._to_domain_entity(session_model) for session_model in queryset]
    
    def update(self, session: UserSession) -> UserSession:
        """Update user session"""
        try:
            session_model = UserSessionModel.objects.get(id=session.id)
            session_model.session_key = session.session_key
            session_model.ip_address = session.ip_address
            session_model.user_agent = session.user_agent
            session_model.country = session.country
            session_model.city = session.city
            session_model.last_activity = session.last_activity
            session_model.is_active = session.is_active
            session_model.save()
            
            return self._to_domain_entity(session_model)
        except UserSessionModel.DoesNotExist:
            raise ValueError(f"Session with id {session.id} does not exist")
    
    def delete(self, session_id: uuid.UUID) -> bool:
        """Delete user session"""
        try:
            session_model = UserSessionModel.objects.get(id=session_id)
            session_model.delete()
            return True
        except UserSessionModel.DoesNotExist:
            return False
    
    def deactivate_session(self, session_id: uuid.UUID) -> bool:
        """Deactivate session"""
        try:
            session_model = UserSessionModel.objects.get(id=session_id)
            session_model.is_active = False
            session_model.save()
            return True
        except UserSessionModel.DoesNotExist:
            return False
    
    def deactivate_user_sessions(self, user_id: uuid.UUID) -> int:
        """Deactivate all sessions for a user"""
        deactivated_count = UserSessionModel.objects.filter(
            user_id=user_id,
            is_active=True
        ).count()
        
        UserSessionModel.objects.filter(
            user_id=user_id,
            is_active=True
        ).update(is_active=False)
        
        return deactivated_count
    
    def delete_expired_sessions(self) -> int:
        """Delete expired sessions and return count"""
        # Delete sessions older than 30 days
        cutoff_date = timezone.now() - timezone.timedelta(days=30)
        expired_count = UserSessionModel.objects.filter(
            last_activity__lt=cutoff_date
        ).count()
        
        UserSessionModel.objects.filter(
            last_activity__lt=cutoff_date
        ).delete()
        
        return expired_count
    
    def _to_domain_entity(self, session_model: UserSessionModel) -> UserSession:
        """Convert Django model to domain entity"""
        return UserSession(
            id=session_model.id,
            user_id=session_model.user_id,
            session_key=session_model.session_key,
            ip_address=session_model.ip_address,
            user_agent=session_model.user_agent,
            country=session_model.country,
            city=session_model.city,
            last_activity=session_model.last_activity,
            is_active=session_model.is_active,
            created_at=session_model.created_at
        ) 