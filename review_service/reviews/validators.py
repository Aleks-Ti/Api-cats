from django.core.exceptions import ValidationError
from django.utils import timezone


def year_validator(value):
    if value > timezone.now().year:
        raise ValidationError(
            message=(
                f'{value} - год выпуска не может быть больше текущего '
                f'Если это анонс произведения, укажите об этом в описании.'
            ),
        )
