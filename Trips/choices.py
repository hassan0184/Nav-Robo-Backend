from django.db import models
from django.utils.translation import gettext as _

class RideStatus(models.TextChoices):
    INITIATED='initiated',_('initiated')  
    ACCEPTED = 'accepted', _('accepted')  
    STARTED = 'started', _('started')
    COMPLETED = 'completed', _('completed')
    CANCELED = 'canceled', _('canceled')
    
class TripFeedback(models.TextChoices):
    HAPPY='happy',_('happy')    
    ANGRY = 'angry', _('angry')
    LIKED = 'liked', _('liked')
    DISLIKED = 'disliked', _('disliked')