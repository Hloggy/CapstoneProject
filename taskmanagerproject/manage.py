#!/usr/bin/env python
import os
import sys
from pathlib import Path

# BASE_DIR = parent of the project folder
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))  # make outer folder importable

def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'taskmanagerproject.settings')
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()

