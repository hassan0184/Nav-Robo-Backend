from rest_framework_nested import routers

from Trips.api.viewsets import TripRelatedView

router = routers.DefaultRouter()

router.register('trips', TripRelatedView, basename='trips')

urlpatterns = router.urls
