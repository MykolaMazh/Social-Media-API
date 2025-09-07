from rest_framework.routers import DefaultRouter

from social_media.views import PostViewSet, TagViewSet, CommentViewSet

router = DefaultRouter()
router.register("posts", PostViewSet)
router.register("tags", TagViewSet)
router.register("comments", CommentViewSet)

urlpatterns = router.urls

app_name = "social_media"
