from django.utils.translation import gettext_lazy as _

SAFETY_TYPE_CHOICES = (
    ('susar', _('SUSAR')),
    ('sae', _('SAE')),
    ('asr', _('Annual Safety Report')),
    ('other', _('Other Safety Report')),
)
