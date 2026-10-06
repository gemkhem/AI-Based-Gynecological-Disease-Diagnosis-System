#!/usr/bin/env python
"""Django's command-line utility for administrative tasks (root wrapper)."""
import os
import sys
from pathlib import Path

# Add fron-end to sys.path so gddes and gddes_app can be imported
BASE_DIR = Path(__file__).resolve().parent / 'fron-end'
sys.path.insert(0, str(BASE_DIR))

def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gddes.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()
