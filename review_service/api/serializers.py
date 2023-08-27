from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
from rest_framework import serializers
from rest_framework.generics import get_object_or_404
from rest_framework.validators import UniqueValidator

from reviews.models import Category, Comment, Genre, Review, Title, User

validators_username = UnicodeUsernameValidator()


class UserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        max_length=150,
        validators=[
            UniqueValidator(queryset=User.objects.all()),
            validators_username,
        ],
    )
    email = serializers.EmailField(
        validators=[
            UniqueValidator(queryset=User.objects.all()),
        ],
        max_length=254,
    )

    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'bio',
            'role',
        )


class UserPatchGetSerializer(UserSerializer):
    class Meta(UserSerializer.Meta):
        model = User
        read_only_fields = ('role',)


class UserRegisterSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        validators=[validators_username],
        max_length=150,
    )
    email = serializers.EmailField(
        max_length=254,
    )

    class Meta:
        model = User
        fields = (
            'username',
            'email',
        )

    def validate_username(self, data):
        if data.lower() == 'me' or data == '':
            raise serializers.ValidationError(
                'Имя "me" или пустое значение, не подходит! Выберите другое!',
            )
        return data

    def validate(self, data):
        if (
            User.objects.filter(username=data['username']).exists()
            and User.objects.get(username=data['username']).email
            != data['email']
        ):
            raise serializers.ValidationError(
                'Неверна указана почта, или логин уже занят!',
            )
        if (
            User.objects.filter(email=data['email']).exists()
            and User.objects.get(email=data['email']).username
            != data['username']
        ):
            raise serializers.ValidationError('Неверный логин')
        return data


class UserTokenSerializer(serializers.Serializer):
    username = serializers.CharField()
    confirmation_code = serializers.CharField()

    class Meta:
        model = User
        fields = (
            'username',
            'confirmation_code',
        )


class AdminTitleSerializer(serializers.ModelSerializer):
    genre = serializers.SlugRelatedField(
        slug_field='slug',
        many=True,
        queryset=Genre.objects.all(),
    )
    category = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Category.objects.all(),
    )

    class Meta:
        fields = (
            'id',
            'name',
            'year',
            'description',
            'genre',
            'category',
        )
        model = Title

    def validate_year(self, data):
        if data > timezone.now().year:
            raise ValidationError(
                message=(
                    f'{data} - год выпуска не может быть больше текущего '
                    f'Если это анонс произведения, укажите об этом в описании.'
                ),
            )
        return data


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'name',
            'slug',
        )
        extra_kwargs = {'url': {'lookup_field': 'slug'}}
        model = Genre


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'name',
            'slug',
        )
        extra_kwargs = {'url': {'lookup_field': 'slug'}}
        model = Category


class TitleSerializer(serializers.ModelSerializer):
    rating = serializers.IntegerField(
        source='reviews__score__avg',
        read_only=True,
    )
    genre = GenreSerializer(many=True)
    category = CategorySerializer()

    class Meta:
        fields = (
            'id',
            'name',
            'year',
            'rating',
            'description',
            'genre',
            'category',
        )
        model = Title


class CommentSerializer(serializers.ModelSerializer):
    review = serializers.SlugRelatedField(slug_field='text', read_only=True)
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
    )

    class Meta:
        model = Comment
        fields = '__all__'


class ReviewSerializer(serializers.ModelSerializer):
    title = serializers.SlugRelatedField(
        slug_field='name',
        read_only=True,
    )
    author = serializers.SlugRelatedField(
        default=serializers.CurrentUserDefault(),
        slug_field='username',
        read_only=True,
    )

    def validate(self, data):
        request = self.context['request']
        author = request.user
        title_id = self.context['view'].kwargs.get('title_id')
        title = get_object_or_404(Title, pk=title_id)
        if request.method == 'POST':
            if Review.objects.filter(title=title, author=author).exists():
                raise ValidationError(
                    'Вы не можете добавить более'
                    'одного отзыва на произведение',
                )
        return data

    class Meta:
        model = Review
        fields = '__all__'
