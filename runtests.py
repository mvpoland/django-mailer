import os
import sys
import warnings

import django

from django.conf import settings
from django.test.runner import DiscoverRunner


warnings.simplefilter("always", DeprecationWarning)


DEFAULT_SETTINGS = dict(
    INSTALLED_APPS=[
        "django.contrib.auth",
        "django.contrib.contenttypes",
        "django.contrib.sites",
        "mailer",
    ],
    DATABASES={
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": ":memory:",
        }
    },
    SITE_ID=1,
    SECRET_KEY="notasecret",
    MIDDLEWARE_CLASSES=[],
)


def runtests(*test_args):
    if not settings.configured:
        settings.configure(**DEFAULT_SETTINGS)

    # Compatibility with Django 1.7's stricter initialization
    if hasattr(django, "setup"):
        django.setup()

    parent = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, parent)

    failures = DiscoverRunner(
        verbosity=1,
        interactive=True,
        failfast=False
    ).run_tests(["mailer.tests"])

    sys.exit(failures)


if __name__ == "__main__":
    runtests()
