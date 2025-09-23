import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'peykan.settings')
django.setup()

from users.models import User

emails = [
    'shb.shahrokh@gmail.com',
    'shahabshahrokh@outlook.com',
    'shahabshahrokhh@gmail.com',
]

for email in emails:
    try:
        user = User.objects.get(email=email)
        user.delete()
        print(f"User with email {email} deleted.")
    except User.DoesNotExist:
        print(f"No user found with email {email}.") 