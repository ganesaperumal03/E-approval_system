"""
WSGI config for rit_e_approval project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application #type:ignore

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rit_e_approval.settings')

application = get_wsgi_application()
