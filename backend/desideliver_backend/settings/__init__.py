"""
Django settings initialization.

This module automatically loads the appropriate settings based on the
DJANGO_SETTINGS_MODULE environment variable.
"""

import os
import sys

# Determine which settings module to use
settings_module = os.environ.get('DJANGO_SETTINGS_MODULE', 'desideliver_backend.settings.local')

# Extract the settings name (local, production, etc.)
settings_name = settings_module.split('.')[-1]

# Import the appropriate settings
if settings_name == 'local':
    from .local import *
elif settings_name == 'production':
    from .production import *
elif settings_name == 'base':
    from .base import *
else:
    # Default to local settings if not specified
    print(f"⚠️  Unknown settings module: {settings_module}. Defaulting to local settings.")
    from .local import *
