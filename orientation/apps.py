from django.apps import AppConfig

from orientation import __version__

class OrientationConfig(AppConfig):
    name = "orientation"
    label = "orientation"
    verbose_name = "aa-orientation V" + __version__

    def ready(self):
        import orientation.signals