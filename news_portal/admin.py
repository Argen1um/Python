from django.contrib import admin
from .models import Category, Post, PostCategory

# создаём новый класс для представления товаров в админке
class PostAdmin(admin.ModelAdmin):
    # list_display — это список или кортеж со всеми полями, которые вы хотите видеть в таблице с товарами
    list_display = ('headline', 'text')
    list_filter = ('author', 'rating')
    search_fields = ('headline', 'text') # тут всё очень похоже на фильтры из запросов в базу

admin.site.register(Category)
admin.site.register(PostCategory)
admin.site.register(Post, PostAdmin)
