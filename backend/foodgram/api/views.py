from typing import Dict
from io import BytesIO
from collections import defaultdict

from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from django.http import FileResponse, JsonResponse

from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from rest_framework.decorators import action
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework import filters, mixins, status, viewsets
from rest_framework.response import Response
from rest_framework.pagination import LimitOffsetPagination

from foodgram.settings import FONT_DIRS
from users.models import User, UsersFollowing
from recipes.models import (
    Ingredients, Recipes, Tags, FavoriteRecipes, ShoppingCart
)
from api.serializers import (
    UserSerializer, UserPasswordSerializer, TagsSerializer,
    IngredientsSerializer, RecipeGetSerializer, RecipePostSerializer,
    UserFavouriteSerializer, RecipeFavoriteSerializer,
)
from api.permissions import (IsAuthor, IsYourShopCart,
                             IsAuthorOrSafeMethodOrAdmin)
from api.utils.custom_filter import (CustomFilterIsFavoritedIsShoppingCart,
                                     CustomRecipesPagination)


class UsersViewset(mixins.CreateModelMixin,
                   mixins.RetrieveModelMixin,
                   mixins.ListModelMixin,
                   viewsets.GenericViewSet):

    queryset = User.objects.all()
    serializer_class = UserSerializer
    http_method_names = ['get', 'post', 'delete']

    @action(detail=False, methods=['get'], url_path='me',
            permission_classes=[IsAuthenticatedOrReadOnly])
    def get_me(self, request):
        return Response(self.get_serializer(request.user).data,
                        status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], url_path='set_password',
            permission_classes=[IsAuthenticated, IsAuthor])
    def update_password(self, request):
        serializer = UserPasswordSerializer(
            context={'request': request.user},
            data=request.data
        )

        serializer.is_valid(raise_exception=True)
        user = request.user
        new_password = serializer.validated_data['new_password']
        user.set_password(new_password)
        user.save()
        return Response(False)

    @action(detail=False, methods=['get', ], url_path='subscriptions',
            permission_classes=[IsAuthenticated])
    def subscribtions(self, request):

        queryset = [follow.following for follow in
                    UsersFollowing.objects.filter(follower=request.user,
                                                  is_follow=True)]
        paginator = LimitOffsetPagination()

        serializer = UserFavouriteSerializer(
            paginator.paginate_queryset(queryset, request),
            many=True,
            context=request.user
        )
        return paginator.get_paginated_response(serializer.data)

    @action(detail=True, methods=['post', 'delete', ], url_path='subscribe',
            permission_classes=[IsAuthenticated])
    def subscribe(self, request, pk=None):

        user_to_follow = get_object_or_404(User, id=pk)

        if request.method == 'POST':
            if not request.user == user_to_follow:
                user_follow, created = UsersFollowing.objects.get_or_create(
                    follower=request.user, following=user_to_follow)
                serializer = UserFavouriteSerializer(request.user,
                                                     context=user_to_follow)

                user_follow.is_follow = True
                user_follow.save()
                return Response(serializer.data, status=status.HTTP_200_OK)

            return Response({'detail': 'You cant subscribe to yourself'},
                            status=status.HTTP_400_BAD_REQUEST)

        else:
            user_following = get_object_or_404(
                UsersFollowing, follower=request.user, following=user_to_follow
            )

            user_following.is_follow = False
            user_following.save()
            return Response(False)


class RecipsViewset(viewsets.ModelViewSet):

    queryset = Recipes.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly,
                          IsAuthorOrSafeMethodOrAdmin)
    http_method_names = ['get', 'post', 'patch', 'delete', ]
    pagination_class = CustomRecipesPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = CustomFilterIsFavoritedIsShoppingCart

    def render_to_response(self, context, **response_kwargs):
        return JsonResponse(list(
            self.get_queryset().values_list('code', flat=True)
        ), safe=False)

    def get_serializer_class(self):
        if self.request.method in ('POST', 'PATCH'):
            return RecipePostSerializer
        return RecipeGetSerializer

    @action(detail=True, methods=['post', 'delete', ], url_path='favorite',
            permission_classes=[IsAuthenticated])
    def favoriting_recipe(self, request, pk=None):

        recipe = get_object_or_404(Recipes, id=pk)

        if request.method == 'POST':

            if not request.user == recipe.author:
                recipese_fav, created = FavoriteRecipes.objects.get_or_create(
                    user_fav=request.user, recipe_fav=recipe)
                serializer = RecipeFavoriteSerializer(recipe)

                recipese_fav.is_follow_rec = True
                recipese_fav.save()
                return Response(serializer.data, status=status.HTTP_200_OK)

            return Response({'detail': 'You cant favourite your own recipes!'},
                            status=status.HTTP_400_BAD_REQUEST)

        else:
            user_fav_rec = get_object_or_404(FavoriteRecipes,
                                             user_fav=request.user,
                                             recipe_fav=recipe)

            user_fav_rec.is_follow_rec = False
            user_fav_rec.save()
            return Response(False)

    @action(detail=False, methods=['get', ],
            url_path='download_shopping_cart',
            permission_classes=[IsAuthenticated, IsYourShopCart])
    def download_shopping_cart(self, request):

        formated_ingredients: Dict[str, int] = defaultdict(int)
        ingredients_amount_tuple = [
            (shopcart.recipe_cart.ingredients.all(),
             shopcart.recipe_cart.ingredientamount.all())
            for shopcart in ShoppingCart.objects.filter(
                user_cart=request.user, is_in_shopping_cart=True
            )
        ]

        for (ingredients, ingredients_amount) in ingredients_amount_tuple:
            for ingredient, ingredient_amount in zip(ingredients,
                                                     ingredients_amount):
                ingredient_str = (f'{ingredient.name} '
                                  f'({ingredient.measurement_unit}) -')
                formated_ingredients[
                    ingredient_str] += ingredient_amount.amount

        styles = getSampleStyleSheet()
        russian_style, styles['Normal'
                              ].fontName = styles['Normal'], 'DejaVuSerif'

        pdfmetrics.registerFont(TTFont('DejaVuSerif',
                                       FONT_DIRS / 'DejaVuSerif.ttf',
                                       'UTF-8'))

        buffer = BytesIO()
        ingredients_pdf = SimpleDocTemplate(
            buffer, pagesize=A4, title='Ingredients',
            author=request.user.username
        )
        story = []

        for ingredient, ingredients_amount in formated_ingredients.items():
            story.append(
                Paragraph(f"{ingredient} {ingredients_amount}", russian_style)
            )
            story.append(Spacer(1, 10))

        ingredients_pdf.build(story)
        buffer.seek(0)

        return FileResponse(buffer, as_attachment=True,
                            filename="ingredients_list.pdf")

    @action(detail=True, methods=['post', 'delete', ],
            url_path='shopping_cart',
            permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, pk=None):

        recipe = get_object_or_404(Recipes, id=pk)

        if request.method == 'POST':
            shopcart, created = ShoppingCart.objects.get_or_create(
                user_cart=request.user, recipe_cart=recipe)
            serializer = RecipeFavoriteSerializer(shopcart.recipe_cart)

            shopcart.is_in_shopping_cart = True
            shopcart.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        else:
            user_fav_rec = get_object_or_404(ShoppingCart,
                                             user_cart=request.user,
                                             recipe_cart=recipe)
            user_fav_rec.is_in_shopping_cart = False
            user_fav_rec.save()
            return Response(False)


class TagsViewset(viewsets.ReadOnlyModelViewSet):
    queryset = Tags.objects.all()
    serializer_class = TagsSerializer
    pagination_class = None


class IngredientsViewset(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredients.objects.all()
    serializer_class = IngredientsSerializer
    pagination_class = None
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']
