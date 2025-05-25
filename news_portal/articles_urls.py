from django.urls import path
# Импортируем созданное нами представление
from .views import (ArticlesList, ArticleDetail, ArticleCreate, ArticleUpdate, ArticleDelete, ArticlesCategoryDetailView,
                    subscribe_to_articles_category, unsubscribe_from_articles_category)
app_name = 'articles'  # Уникальный app_name для статей
urlpatterns = [
   # Т.к. наше объявленное представление является классом,
   # а Django ожидает функцию, нам надо представить этот класс в виде view.
   # Для этого вызываем метод as_view.
   path('', ArticlesList.as_view(), name='list'),
   # pk — это первичный ключ товара, который будет выводиться у нас в шаблон
   # int — указывает на то, что принимаются только целочисленные значения
   path('<int:pk>', ArticleDetail.as_view(), name='detail'),
   path('create/', ArticleCreate.as_view(), name='create'),
   # path('search/', ArticleSearch.as_view(), name='search'),
   path('<int:pk>/update/', ArticleUpdate.as_view(), name='update'),
   path('<int:pk>/delete/', ArticleDelete.as_view(), name='delete'),

   path('category/<int:pk>/', ArticlesCategoryDetailView.as_view(), name='articles_category_detail'),
   path('category/<int:pk>/subscribe/', subscribe_to_articles_category, name='subscribe_articles_category'),
   path('category/<int:pk>/unsubscribe/', unsubscribe_from_articles_category, name='unsubscribe_articles_category'),
]