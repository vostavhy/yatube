from django.urls import path, include

from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.routers import DefaultRouter

from .views import PostViewSet, CommentViewSet, GroupViewSet, FollowViewSet

router = DefaultRouter()
router.register('v1/posts', PostViewSet)
router.register(r'v1/posts/(?P<post_id>\d+)/comments', CommentViewSet)

router.register('v1/group', GroupViewSet)
router.register('v1/follow', FollowViewSet)

urlpatterns = [
        path('', include(router.urls)),
        path('v1/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
        path('v1/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    ]
