from django.apps import apps
from django.test import SimpleTestCase


class IdeasAppConfigTests(SimpleTestCase):
    def test_ideas_app_is_installed(self) -> None:
        app_config = apps.get_app_config("ideas")

        self.assertEqual(app_config.name, "ideas")
