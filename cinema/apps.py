from django.apps import AppConfig


class CinemaConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'cinema'

    def ready(self):
        import cinema.signals  # اینجا فایل سیگنال‌ها رو وارد کن
