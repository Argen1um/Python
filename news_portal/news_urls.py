from django.urls import path
# Импортируем созданное нами представление
from .views import NewsList, NewSearch, NewDetail, NewCreate, NewUpdate, NewDelete
app_name = 'news'  # Уникальный app_name для новостей
urlpatterns = [
   # Т.к. наше объявленное представление является классом,
   # а Django ожидает функцию, нам надо представить этот класс в виде view.
   # Для этого вызываем метод as_view.
   path('', NewsList.as_view(), name='news_list'),
   # pk — это первичный ключ товара, который будет выводиться у нас в шаблон
   # int — указывает на то, что принимаются только целочисленные значения
   path('<int:pk>', NewDetail.as_view(), name='new_detail'),
   path('create/', NewCreate.as_view(), name='new_create'),
   path('search/', NewSearch.as_view(), name='new_search'),
   path('<int:pk>/update/', NewUpdate.as_view(), name='new_update'),
   path('<int:pk>/delete/', NewDelete.as_view(), name='new_delete'),
]