from django_filters import rest_framework

from rest_framework.pagination import PageNumberPagination

from recipes.models import Recipes


class CustomRecipesPagination(PageNumberPagination):
    page_query_param = 'page'
    page_size_query_param = 'limit'
    max_page_size = 100
    page_size = 6


class CustomFilterIsFavoritedIsShoppingCart(rest_framework.FilterSet):

    tags = rest_framework.AllValuesMultipleFilter(
        field_name='tags__slug',
        label='Теги'
    )
    is_favorited = rest_framework.BooleanFilter(
        field_name='favourite', method='get_is_favorited', label='Избранное')
    is_in_shopping_cart = rest_framework.BooleanFilter(
        field_name='shopcart', method='get_is_in_shopping_cart',
        label='В корзине')
    author = rest_framework.AllValuesMultipleFilter(
        field_name='author__id', label='Автор')

    class Meta:
        model = Recipes
        fields = ('tags', 'author', 'is_favorited', 'is_in_shopping_cart')

    def get_is_favorited(self, queryset, name, value):
        if value and self.request.user.is_authenticated:
            return queryset.filter(
                favourite__user_fav=self.request.user,
                favourite__is_follow_rec=True
            )
        return queryset

    def get_is_in_shopping_cart(self, queryset, name, value):
        if value and self.request.user.is_authenticated:
            return queryset.filter(
                shopcart__user_cart=self.request.user,
                shopcart__is_in_shopping_cart=True
            )
        return queryset
