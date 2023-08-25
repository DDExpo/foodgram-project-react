from django.contrib import admin

from users.models import User, UsersFollowing
from recipes.models import (Ingredients, ShoppingCart, IngredientAmount,
                            Tags, Recipes, FavoriteRecipes)


class AdminFGUser(admin.ModelAdmin):
    list_display = (
        '__str__',
        'username',
        'first_name',
        'last_name',
        'email',
    )
    list_editable = ('username', 'email',
                     'first_name', 'last_name', )
    search_fields = ('username', 'email', )
    list_filter = ('username', 'email', )
    empty_value_display = '-пусто-'


class AdminIngredientsInLine(admin.TabularInline):
    model = IngredientAmount
    extra = 1


class AdminRecipes(admin.ModelAdmin):
    list_display = (
        '__str__',
        'name',
        'author',
        'text',
        'cooking_time',
    )

    list_editable = ('name', 'author', )
    search_fields = ('name', 'author', 'tags',)
    list_filter = ('name', 'author', )
    inlines = [AdminIngredientsInLine]
    empty_value_display = '-пусто-'


class AdminTags(admin.ModelAdmin):
    list_display = (
        '__str__',
        'name',
        'color',
        'slug',
    )
    list_editable = ('name', 'color', 'slug')
    prepopulated_fields = {'slug': ('name', )}
    search_fields = ('name', 'color', 'slug', )
    list_filter = ('name', 'slug', )
    empty_value_display = '-пусто-'


class AdminIngredients(admin.ModelAdmin):
    list_display = (
        '__str__',
        'name',
        'measurement_unit',
    )
    search_fields = ('name', )
    list_filter = ('name', )
    empty_value_display = '-пусто-'


class AdminFavouriteRecipes(admin.ModelAdmin):
    list_display = (
        '__str__',
        'recipe_fav',
        'user_fav',
        'born_at',
    )
    search_fields = ('user_fav', )
    list_filter = ('user_fav', 'born_at')
    empty_value_display = '-пусто-'


class AdminShoppingCart(admin.ModelAdmin):
    list_display = (
        '__str__',
        'user_cart',
        'recipe_cart',
        'is_in_shopping_cart',
        'added_at',
    )
    search_fields = ('user_cart', )
    list_filter = ('user_cart', 'is_in_shopping_cart', 'added_at', )
    empty_value_display = '-пусто-'


class AdminUsersFollowing(admin.ModelAdmin):
    list_display = (
        '__str__',
        'following',
        'follower',
        'created_at',
        'is_follow',
    )
    search_fields = ('following', 'follower', )
    list_filter = ('following', 'follower', 'created_at', )
    empty_value_display = '-пусто-'


admin.site.register(User, AdminFGUser)
admin.site.register(Recipes, AdminRecipes)
admin.site.register(Tags, AdminTags)
admin.site.register(Ingredients, AdminIngredients)
admin.site.register(FavoriteRecipes, AdminFavouriteRecipes)
admin.site.register(ShoppingCart, AdminShoppingCart)
admin.site.register(UsersFollowing, AdminUsersFollowing)
