from django.db import models
from django.utils.translation import gettext as _

class OperatorStatus(models.TextChoices):
    ONLINE = 'Online', _('Online')
    OFFLINE = 'Offline', _('Offline')
