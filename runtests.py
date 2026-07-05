"""Minimal test runner for django-stocks."""
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

os.environ["DJANGO_SETTINGS_MODULE"] = "tests.settings"

import django
django.setup()

from django.test.runner import DiscoverRunner

runner = DiscoverRunner(verbosity=2)
failures = runner.run_tests(["tests"])
sys.exit(bool(failures))
