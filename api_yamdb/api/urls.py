from django.urls import include, path
from rest_framework import routers

from api.views import (
    CategoryViewSet,
    CommentViewSet,
    GenreViewSet,
    ReviewViewSet,
    TitleViewSet,
    UserViewSet,
    get_tokens_for_user,
    register_user,
)

router = routers.DefaultRouter()
router.register('users', UserViewSet, basename='users')
router.register('titles', TitleViewSet, basename='titles')
router.register('categories', CategoryViewSet, basename='categories')
router.register('genres', GenreViewSet, basename='genres')
router.register(
    r'categories/(^[-a-zA-Z0-9_]+$\d+)/',
    CategoryViewSet,
    basename='categories',
)
router.register(
    r'genres/(^[-a-zA-Z0-9_]+$\d+)/',
    GenreViewSet,
    basename='genres',
)
router.register(
    r'titles/(?P<title_id>\d+)/reviews',
    ReviewViewSet,
    basename='reviews',
)
router.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)' r'/comments',
    CommentViewSet,
    basename='comments',
)


urlpatterns = [
    path('v1/', include(router.urls)),
    path('v1/auth/signup/', register_user, name='user_signup'),
    path('v1/auth/token/', get_tokens_for_user, name='get_token'),
]
