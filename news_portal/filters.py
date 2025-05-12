from django_filters import FilterSet, CharFilter, DateFilter
from django import forms
from .models import Post

# Создаем свой набор фильтров для модели Post.
# FilterSet, который мы наследуем,
class PostFilter(FilterSet):
    headline = CharFilter(
        field_name='headline',
        lookup_expr='icontains',
        label='по названию'
    )
    author = CharFilter(
        field_name='author__user__username',
        lookup_expr='icontains',
        label='по автору'
    )
    time_in = DateFilter(
        field_name='time_in',
        lookup_expr='gt',
        label='позже указываемой даты:',
        widget=forms.DateInput(attrs={'type': 'date'})  # Виджет для выбора даты
    )

    class Meta:
        model = Post
        fields = ['headline', 'author']