from django.apps import AppConfig
from django_mdmail import convert_md_templates

class CoreConfig(AppConfig):
    name = 'core'

    # A function that is run by Django at server startup (not per page hit).
    def ready(self):
        # Converts markdown templates (`.md`) into plaintext (`.txt`) and HTML (`.html`) templates.
        convert_md_templates()
