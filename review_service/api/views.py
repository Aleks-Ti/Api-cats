from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db.models import Avg
from django.http import HttpRequest
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken

from api.filters import TitleFilter
from api.mixins import CreateListDestroyViewSet
from api.permissions import (
    AdminOnly,
    AdminOrReadOnly,
    IsAdminModeratorOwnerOrReadOnly,
)
from api.serializers import (
    AdminTitleSerializer,
    CategorySerializer,
    CommentSerializer,
    GenreSerializer,
    ReviewSerializer,
    TitleSerializer,
    UserPatchGetSerializer,
    UserRegisterSerializer,
    UserSerializer,
    UserTokenSerializer,
)
from reviews.models import Category, Genre, Review, Title, User


class UserViewSet(viewsets.ModelViewSet):
    http_method_names = ['get', 'post', 'delete', 'patch']
    lookup_field = 'username'
    filter_backends = (filters.SearchFilter,)
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (AdminOnly,)
    pagination_class = PageNumberPagination
    search_fields = ('username',)

    @action(
        methods=['get', 'patch'],
        url_path='me',
        detail=False,
        permission_classes=[permissions.IsAuthenticated],
        serializer_class=UserPatchGetSerializer,
    )
    def user_profile(self, request: HttpRequest):
        user = request.user
        if request.method == 'GET':
            serializers = self.get_serializer(user)
            return Response(serializers.data, status=status.HTTP_200_OK)
        serializers = self.get_serializer(
            user,
            data=request.data,
            partial=True,
        )
        serializers.is_valid(raise_exception=True)
        serializers.save()
        return Response(serializers.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def register_user(request: HttpRequest):
    serializers = UserRegisterSerializer(data=request.data)
    serializers.is_valid(raise_exception=True)
    user, _ = User.objects.get_or_create(
        username=serializers.validated_data['username'],
        email=serializers.validated_data['email'],
    )
    confirmation_code = default_token_generator.make_token(user)
    send_mail(
        subject=(f'Welcome on the portal Yambd! {user}!'),
        message=(
            f'Добро пожаловать {user}! 🥳\n'
            f'Ваш ключ верификации: {confirmation_code}\n'
            f'Никому его не показывайте и не передавайте третьим лицам!'
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )
    return Response(serializers.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def get_tokens_for_user(request: HttpRequest):
    serializers = UserTokenSerializer(data=request.data)
    serializers.is_valid(raise_exception=True)
    username = serializers.validated_data['username']
    confirmation_code = serializers.validated_data['confirmation_code']
    user = get_object_or_404(User, username=username)
    if default_token_generator.check_token(user, confirmation_code):
        token = AccessToken.for_user(user)
        return Response({'token': str(token)}, status=status.HTTP_200_OK)

    return Response(serializers.errors, status=status.HTTP_400_BAD_REQUEST)


class GenreViewSet(CreateListDestroyViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class CategoryViewSet(CreateListDestroyViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all().annotate(Avg('reviews__score'))
    serializer_class = AdminTitleSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter
    permission_classes = (AdminOrReadOnly,)

    def get_serializer_class(self):
        if (
            not self.request.user.is_authenticated
            or self.request.method in permissions.SAFE_METHODS
        ):
            return TitleSerializer
        return self.serializer_class


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [IsAdminModeratorOwnerOrReadOnly]

    def get_queryset(self):
        title = get_object_or_404(Title, pk=self.kwargs.get('title_id'))
        return title.reviews.all()

    def perform_create(self, serializer):
        title_id = self.kwargs.get('title_id')
        title = get_object_or_404(Title, id=title_id)
        serializer.save(author=self.request.user, title=title)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [IsAdminModeratorOwnerOrReadOnly]

    def get_queryset(self):
        review = get_object_or_404(Review, pk=self.kwargs.get('review_id'))
        return review.comments.all()

    def perform_create(self, serializer):
        title_id = self.kwargs.get('title_id')
        review_id = self.kwargs.get('review_id')
        review = get_object_or_404(Review, id=review_id, title=title_id)
        serializer.save(author=self.request.user, review=review)
