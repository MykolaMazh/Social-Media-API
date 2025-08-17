from rest_framework.routers import DefaultRouter

from social_media.views import PostViewSet, TagViewSet

router = DefaultRouter()
router.register("posts", PostViewSet)
router.register("tags", TagViewSet)

urlpatterns = router.urls

app_name = "social_media"
