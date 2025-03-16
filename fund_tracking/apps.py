from django.apps import AppConfig


class FundTrackingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'fund_tracking'

    def ready(self):
        import fund_tracking.signals