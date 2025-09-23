import os
import sys


def main() -> None:
    # Ensure project root is on sys.path
    base_dir = os.path.dirname(os.path.abspath(__file__))
    if base_dir not in sys.path:
        sys.path.insert(0, base_dir)

    # Configure Django settings
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'peykan.settings')

    # Initialize Django
    import django  # type: ignore
    django.setup()

    # Import and run seed functions
    from create_test_data import (
        create_test_users,
        create_tour_test_data,
        create_event_test_data,
        create_transfer_test_data,
    )

    create_test_users()
    create_tour_test_data()
    create_event_test_data()
    create_transfer_test_data()

    print('SEED_OK')


if __name__ == '__main__':
    main()


