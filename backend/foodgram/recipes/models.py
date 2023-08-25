from typing import List

from django.db import models
from django.core.validators import RegexValidator
from django.core.validators import MaxValueValidator, MinValueValidator

from users.models import User

MODELS_FIELDS: List[str] = ['name', 'slug', 'color', 'measurement_unit']
REGEX_VALIDATOR_RECIPE = RegexValidator(regex=r'^[-a-zA-Z0-9_]+$')


class Tags(models.Model):

    name = models.CharField(
        db_index=True, verbose_name='Название', max_length=200,
        unique=True, blank=False)
    color = models.CharField(
        verbose_name='Цвет',
        help_text='HEX код: #49B64E',
        default='#FF0000',
        max_length=7, unique=True,
        blank=False,
    )
    slug = models.SlugField(verbose_name='Слаг',
                            blank=False, unique=True, max_length=200,
                            validators=[REGEX_VALIDATOR_RECIPE, ])

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ('slug', )

    def __str__(self):
        return self.name


class Ingredients(models.Model):

    name = models.CharField(db_index=True, verbose_name='Название',
                            max_length=200, unique=False)

    measurement_unit = models.CharField(
        verbose_name='Единицы измерения', help_text='шт', max_length=200)

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        constraints = [
            models.UniqueConstraint(fields=['name', 'measurement_unit'],
                                    name='unique_ingredients')
        ]
        ordering = ('name', )

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'


class Recipes(models.Model):

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор рецепта',
        blank=False,
        max_length=150,
    )

    name = models.CharField(
        verbose_name='Название рецепта', blank=False, null=True,
        help_text='Будьте креативными!', max_length=200
    )

    image = models.ImageField(upload_to='recipes/images/', blank=False,
                              null=True, default=None, verbose_name='Картинка')
    text = models.TextField(
        verbose_name='Описание', max_length=999,
        blank=False, null=True
    )
    ingredients = models.ManyToManyField(
        Ingredients,
        through='IngredientAmount',
        related_name='recipes',
        verbose_name='ингредиенты'

    )
    tags = models.ManyToManyField(
        Tags,
        related_name='recipes',
        verbose_name='Теги'
    )

    cooking_time = models.IntegerField(
        verbose_name='Время приготовления(в минутах)', blank=False, default=1,
        validators=[MinValueValidator(1), MaxValueValidator(9999)]
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-created_at', )

    def __str__(self):
        return f'рецепт: {self.name}, автора: {self.author}'


class IngredientAmount(models.Model):

    ingredient = models.ForeignKey(
        Ingredients,
        on_delete=models.CASCADE,
        blank=False,
        verbose_name='ингредиент',
        related_name='ingredientamount'
    )
    recipe = models.ForeignKey(
        Recipes,
        on_delete=models.CASCADE,
        blank=False,
        verbose_name='рецепт',
        related_name='ingredientamount'
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='количество',
        blank=False,
        validators=[
            MinValueValidator(
                1,
            ),
            MaxValueValidator(
                9999,
            )
        ],
    )

    class Meta:
        verbose_name = 'Количество Ингредиентов'
        verbose_name_plural = 'Количество Ингредиентов'

    def __str__(self):
        return str(self.amount)


class ShoppingCart(models.Model):

    user_cart = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopcart',
        verbose_name='Юзер',
        blank=False,
        max_length=150
    )
    recipe_cart = models.ForeignKey(
        Recipes,
        on_delete=models.CASCADE,
        related_name='shopcart',
        verbose_name='Рецепт',
        blank=False,
        max_length=150
    )

    is_in_shopping_cart = models.BooleanField(default=False)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзина'
        ordering = ('-added_at', )
        constraints = [
            models.UniqueConstraint(fields=['recipe_cart', 'user_cart'],
                                    name='unique_shop_cart')
        ]

    def __str__(self):
        return f'рецепт {self.recipe_cart} в корзине {self.user_cart}'


class FavoriteRecipes(models.Model):

    recipe_fav = models.ForeignKey(
        Recipes, verbose_name=('Избранный рецепт'), blank=False,
        related_name='favourite', on_delete=models.CASCADE)

    user_fav = models.ForeignKey(
        User, verbose_name='Юзер', blank=False,
        related_name='favourite', on_delete=models.CASCADE
    )

    is_follow_rec = models.BooleanField(default=False)

    born_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        ordering = ('-born_at', )
        constraints = [
            models.UniqueConstraint(fields=['recipe_fav', 'user_fav'],
                                    name='unique_recipe_fav'),
            models.CheckConstraint(check=~models.Q(
                user_fav=models.F('recipe_fav')),
                name='no_self_fav_recipe'
            )
        ]

    def __str__(self):
        return self.recipe_fav.__str__()
