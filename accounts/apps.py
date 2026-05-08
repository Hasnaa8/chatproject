from django.apps import AppConfig
from django.contrib.admin.apps import AdminConfig


class AccountsConfig(AppConfig):
    name = 'accounts'
    
    def ready(self):
        import accounts.signals  # Add this line to import the signals.py
