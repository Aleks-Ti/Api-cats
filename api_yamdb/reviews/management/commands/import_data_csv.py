import csv
import os
from typing import Any

from django.core.management.base import BaseCommand
from django.db import IntegrityError

from reviews.models import Category, Comment, Genre, Review, Title, User


class bcolors:
    HEADER = '\033[95m'
    OK_BLUE = '\033[94m'
    OK_CYAN = '\033[96m'
    OK_GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


FILES = {
    User: 'users.csv',
    Category: 'category.csv',
    Genre: 'genre.csv',
    Title: 'titles.csv',
    Review: 'review.csv',
    Comment: 'comments.csv',
}


class Command(BaseCommand):
    def get_category_id(id):
        pass

    def handle(self, *args: Any, **options: Any) -> str | None:
        del args, options
        path_up_dir_project = os.getcwd()
        for models, files in FILES.items():
            path_csv_files = os.path.join(
                path_up_dir_project,
                'api_yamdb',
                'static',
                'data',
                files,
            )
            with open(file=path_csv_files, mode='r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    try:
                        model_write, create = models.objects.get_or_create(
                            **row,
                        )
                        if not create:
                            model_write = models.objects.update(**row)
                            print(
                                bcolors.OK_BLUE
                                + 'данные обновлены'
                                + bcolors.ENDC,
                            )
                        model_write.save()
                    except IntegrityError as err:
                        print(
                            f'{bcolors.WARNING}{err} - данные в '
                            f'таблице {models.__name__} '
                            f'или уже существуют, или не валидные',
                        )
        print(bcolors.OK_GREEN + 'Работа завершена')
