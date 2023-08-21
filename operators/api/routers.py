from rest_framework_nested import routers

from operators.api.viewsets import OperatorViewSet

router = routers.DefaultRouter()

router.register('operator', OperatorViewSet, basename='operator')

# URLConf
urlpatterns = router.urls
