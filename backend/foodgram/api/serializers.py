from collections import defaultdict

from django.db import transaction

from rest_framework import serializers

from drf_extra_fields.fields import Base64ImageField

from djoser.serializers import UserCreateSerializer
from users.models import User, UsersFollowing
from recipes.models import (Recipes, Tags, Ingredients,
                            IngredientAmount)


class UserRecipeSerializer(serializers.ModelSerializer):

    image = Base64ImageField(use_url=True, label='Картинка')

    class Meta:
        model = Recipes
        fields = ['id', 'name', 'image', 'cooking_time', ]
        read_only_fields = ('id', 'name', 'image', 'cooking_time', )


class UserSerializer(UserCreateSerializer):

    is_subscribed = serializers.SerializerMethodField()
    password = serializers.CharField(write_only=True, label=('Пароль'))

    def get_is_subscribed(self, instance):
        if not self.context['request'].user.is_anonymous:
            return UsersFollowing.objects.filter(
                follower=self.context['request'].user,
                following=instance,
                is_follow=True,
            ).exists()
        return False

    class Meta:
        model = User
        read_only_fields = ('id', 'is_subscribed', )
        fields = ['username', 'email', 'is_subscribed', 'password',
                  'first_name', 'last_name', 'id', ]


class UserPasswordSerializer(serializers.Serializer):

    current_password = serializers.CharField(write_only=True, required=True)
    new_password = serializers.CharField(write_only=True, required=True)

    def validate_current_password(self, value):
        if not self.context['request'].check_password(value):
            raise serializers.ValidationError("Old password is incorrect.")
        return value


class UserFavouriteSerializer(serializers.ModelSerializer):

    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()
    is_subscribed = serializers.SerializerMethodField()

    def get_is_subscribed(self, instance):
        return UsersFollowing.objects.filter(follower=self.context,
                                             following=instance,
                                             is_follow=True).exists()

    def get_recipes(self, instance):
        return UserRecipeSerializer(Recipes.objects.filter(author=instance),
                                    many=True).data

    def get_recipes_count(self, instance):
        return Recipes.objects.filter(author=instance).count()

    class Meta:
        model = User
        fields = ['email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed', 'recipes', 'recipes_count']
        read_only_fields = ('email', 'id', 'username', 'first_name',
                            'last_name', 'is_subscribed', 'recipes',
                            'recipes_count', )


class TagsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tags
        fields = ['id', 'name', 'color', 'slug', ]
        read_only_fields = ('name', 'color', 'slug', )


class IngredientsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredients
        fields = ['id', 'name', 'measurement_unit']
        read_only_fields = ('id', 'name', 'measurement_unit',)


class IngredientAmountRecipePostSerializer(serializers.ModelSerializer):

    id = serializers.PrimaryKeyRelatedField(queryset=Ingredients.objects.all())

    class Meta:
        model = IngredientAmount
        fields = ('id', 'amount',)

    def to_representation(self, instance):

        return {
            'id': IngredientsSerializer(instance).data['id'],
            'amount': [ingredient_amount.amount for ingredient_amount
                       in instance.ingredientamount.all()]
        }


class RecipeGetSerializer(serializers.ModelSerializer):

    tags = TagsSerializer(many=True, read_only=True)
    author = UserSerializer(read_only=True)
    image = Base64ImageField(use_url=True, label='Картинка')
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipes
        fields = [
            'id', 'tags', 'ingredients', 'author', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time',
        ]
        read_only_fields = (
            'id', 'tags', 'ingredients', 'author', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time',
        )

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        ingredients_with_amount = []

        for ingredient_amount in instance.ingredientamount.all(
        ).prefetch_related('ingredient'):
            ingredient = ingredient_amount.ingredient
            ingredients_with_amount.append({
                'id': ingredient.id,
                'name': ingredient.name,
                'measurement_unit': ingredient.measurement_unit,
                'amount': ingredient_amount.amount
            })

        representation['ingredients'] = ingredients_with_amount
        return representation

    def get_is_favorited(self, object):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return object.favourite.filter(user_fav=request.user,
                                       is_follow_rec=True).exists()

    def get_is_in_shopping_cart(self, object):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return object.shopcart.filter(user_cart=request.user,
                                      is_in_shopping_cart=True).exists()


class RecipePostSerializer(serializers.ModelSerializer):

    ingredients = IngredientAmountRecipePostSerializer(many=True)
    image = Base64ImageField(use_url=True, label='Картинка')

    class Meta:
        model = Recipes
        fields = ['id', 'tags', 'ingredients', 'image',
                  'name', 'text', 'cooking_time', ]

    @transaction.atomic
    def update(self, instance, validated_data):

        self.is_valid(raise_exception=True)

        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get('cooking_time',
                                                   instance.cooking_time)
        ingredient_data = validated_data.get('ingredients')
        tags_data = validated_data.get('tags')

        instance.tags.set(tags_data)

        instance.ingredientamount.all().delete()

        instance.ingredientamount.add(
            IngredientAmount.objects.bulk_create(
                [IngredientAmount(
                    ingredient=ingredient['id'],
                    recipe=instance,
                    amount=ingredient['amount']
                ) for ingredient in ingredient_data]
            )
        )

        instance.save()
        return instance

    @transaction.atomic
    def create(self, validated_data):

        self.is_valid(raise_exception=True)

        formated_ingredients = defaultdict(int)
        ingredient_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')

        recipe = Recipes.objects.create(
            author=self.context.get('request').user, **validated_data
        )

        recipe.tags.set(tags_data)

        for ingredient in ingredient_data:
            formated_ingredients[ingredient['id']] += ingredient['amount']

            recipe.ingredientamount.add(
                IngredientAmount.objects.bulk_create(
                    [IngredientAmount(
                        ingredient=ingredient,
                        recipe=recipe,
                        amount=ingredient_amount
                    ) for ingredient, ingredient_amount
                      in formated_ingredients.items()]
                )
            )

        return recipe


class RecipeFavoriteSerializer(serializers.ModelSerializer):

    image = Base64ImageField(use_url=True, label='Картинка')

    class Meta:
        model = Recipes
        fields = ['name', 'image', 'text', 'cooking_time', ]
