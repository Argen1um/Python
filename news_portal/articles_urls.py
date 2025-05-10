from django.urls import path
# Импортируем созданное нами представление
from .views import ArticlesList, ArticleDetail, ArticleCreate, ArticleUpdate, ArticleDelete
app_name = 'articles'  # Уникальный app_name для статей
urlpatterns = [
   # Т.к. наше объявленное представление является классом,
   # а Django ожидает функцию, нам надо представить этот класс в виде view.
   # Для этого вызываем метод as_view.
   path('', ArticlesList.as_view(), name='articles_list'),
   # pk — это первичный ключ товара, который будет выводиться у нас в шаблон
   # int — указывает на то, что принимаются только целочисленные значения
   path('<int:pk>', ArticleDetail.as_view(), name='article_detail'),
   path('create/', ArticleCreate.as_view(), name='article_create'),
   #path('search/', PostSearch.as_view(), name='post_search'),
   path('<int:pk>/update/', ArticleUpdate.as_view(), name='article_update'),
   path('<int:pk>/delete/', ArticleDelete.as_view(), name='article_delete'),
]