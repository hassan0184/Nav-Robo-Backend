from rest_framework_nested import routers

from rider.api.viewsets import RiderViewSet

router = routers.DefaultRouter()

router.register('rider', RiderViewSet, basename='rider')

# URLConf
urlpatterns = router.urls
