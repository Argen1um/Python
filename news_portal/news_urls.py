from django.urls import path
# Импортируем созданное нами представление
from .views import (NewsList, NewSearch, NewDetail, NewCreate, NewUpdate, NewDelete, NewsCategoryDetailView,
                    subscribe_to_news_category, unsubscribe_from_news_category)
app_name = 'news'  # Уникальный app_name для новостей
urlpatterns = [
   # Т.к. наше объявленное представление является классом,
   # а Django ожидает функцию, нам надо представить этот класс в виде view.
   # Для этого вызываем метод as_view.
   path('', NewsList.as_view(), name='list'),
   # pk — это первичный ключ товара, который будет выводиться у нас в шаблон
   # int — указывает на то, что принимаются только целочисленные значения
   path('<int:pk>', NewDetail.as_view(), name='detail'),
   path('create/', NewCreate.as_view(), name='create'),
   path('search/', NewSearch.as_view(), name='search'),
   path('<int:pk>/update/', NewUpdate.as_view(), name='update'),
   path('<int:pk>/delete/', NewDelete.as_view(), name='delete'),

   path('category/<int:pk>/', NewsCategoryDetailView.as_view(), name='news_category_detail'),
   path('category/<int:pk>/subscribe/', subscribe_to_news_category, name='subscribe_news_category'),
   path('category/<int:pk>/unsubscribe/', unsubscribe_from_news_category, name='unsubscribe_news_category'),
]