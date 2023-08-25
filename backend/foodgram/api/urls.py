from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import (IngredientsViewset, RecipsViewset, TagsViewset,
                       UsersViewset)

app_name = 'api'

router_v1 = DefaultRouter()

router_v1.register('recipes', RecipsViewset, basename='recipes')
router_v1.register('users', UsersViewset, basename='users')
router_v1.register('ingredients', IngredientsViewset, basename='ingredients')
router_v1.register('tags', TagsViewset, basename='tags')

urlpatterns = [
    path('', include(router_v1.urls)),
    path('auth/', include('djoser.urls.authtoken')),
]
