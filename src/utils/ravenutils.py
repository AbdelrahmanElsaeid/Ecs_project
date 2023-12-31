
from sentry_sdk import configure_scope
from django.conf import settings
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

sentry_sdk.init(
    dsn=settings.YOUR_SENTRY_DSN,
    integrations=[DjangoIntegration()],
    release=settings.ECS_VERSION,
    environment=settings.ENVIRONMENT,
    send_default_pii=True
)

class DjangoClient(DjangoIntegration):
    def build_msg(self, *args, **kwargs):
        with configure_scope() as scope:
            # Add custom tags and extra data to the scope
            scope.set_tag('branch', settings.ECS_GIT_BRANCH)
            scope.set_extra('version', settings.ECS_VERSION)

        # Return the modified data
        return super().build_msg(*args, **kwargs)






#

    