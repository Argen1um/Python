from django.http import Http404
from django.shortcuts import render
from django.urls import reverse_lazy
from django.contrib.auth.mixins import PermissionRequiredMixin

from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView
)
from .models import Post
from .forms import PostForm
from .filters import PostFilter
from pprint import pprint
from .resources import POSITIONS

class BasePostListView(ListView):
    """Базовый класс для всех списков публикаций"""
    context_object_name = 'posts'
    paginate_by = 10
    publication_type = None  # Для фильтрации по типу
    use_filters = False  # Нужна ли фильтрация
    default_ordering = '-time_in'
    prefetch_related = ['categories']  # Оптимизация запросов

    def get_base_queryset(self):
        """Базовый QuerySet без фильтрации"""
        queryset = Post.objects.all()
        if self.publication_type:
            queryset = queryset.filter(publication_type=self.publication_type)
        if self.default_ordering:
            queryset = queryset.order_by(self.default_ordering)
        if self.prefetch_related:
            queryset = queryset.prefetch_related(*self.prefetch_related)
        return queryset

    def get_queryset(self):
        """Основной метод получения QuerySet с учетом фильтров"""
        queryset = self.get_base_queryset()
        if self.use_filters:
            self.filterset = PostFilter(self.request.GET, queryset=queryset)
            return self.filterset.qs
        return queryset

    def get_context_data(self, **kwargs):
        """Добавляем в контекст общие и специфические данные"""
        context = super().get_context_data(**kwargs)
        context['time_sensation'] = None  # Общая переменная
        if self.use_filters:
            context['filterset'] = self.filterset

        return context

class NewsList(BasePostListView):
    template_name = 'news.html'
    publication_type = 'NE'

class ArticlesList(BasePostListView):
    template_name = 'articles.html'
    publication_type = 'AR'

class NewSearch(BasePostListView):
    """Поиск по новостям"""
    template_name = 'news_search.html'
    publication_type = 'NE'
    use_filters = True

# class NewsList(ListView):
#     template_name = 'news.html'
#     context_object_name = 'posts'
#     paginate_by = 10
#
#     def get_queryset(self):
#         return Post.objects.filter(publication_type='NE').order_by('-time_in').prefetch_related('categories')
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['time_sensation'] = None
#         # pprint(context)
#         return context
#
# class ArticlesList(ListView):
#     template_name = 'articles.html'
#     context_object_name = 'posts'
#     paginate_by = 10
#
#     def get_queryset(self):
#         return Post.objects.filter(publication_type='AR').order_by('-time_in').prefetch_related('categories')
#
# class NewSearch(ListView):
#     queryset = (Post.objects\
#         .order_by('-time_in')\
#         .prefetch_related('categories')
#         .filter(publication_type='NE'))
#     template_name = 'news_search.html'
#     context_object_name = 'posts'
#     paginate_by = 10
#
#     # Переопределяем функцию получения списка публикаций
#     def get_queryset(self):
#         # Получаем обычный запрос
#         queryset = super().get_queryset()
#         # Используем наш класс фильтрации.
#         # self.request.GET содержит объект QueryDict, который мы рассматривали
#         # в этом юните ранее.
#         # Сохраняем нашу фильтрацию в объекте класса,
#         # чтобы потом добавить в контекст и использовать в шаблоне.
#         self.filterset = PostFilter(self.request.GET, queryset)
#         # Возвращаем из функции отфильтрованный список публикаций
#         return self.filterset.qs
#
#     # Метод get_context_data позволяет нам изменить набор данных,
#     # который будет передан в шаблон.
#     def get_context_data(self, **kwargs):
#         # С помощью super() мы обращаемся к родительским классам
#         # и вызываем у них метод get_context_data с теми же аргументами,
#         # что и были переданы нам.
#         # В ответе мы должны получить словарь.
#         context = super().get_context_data(**kwargs)
#         context['filterset'] = self.filterset
#         # pprint(context)
#         return context

class BasePostDetail(DetailView):
    model = Post
    template_name = 'post.html'
    context_object_name = 'post'
    publication_type = None
    error_message = "Запись не соответствует типу (ожидался: {})"

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if obj.publication_type != self.publication_type:
            raise Http404(self.error_message.format(self.publication_type))
        return obj

class NewDetail(BasePostDetail):
    """Детальное отображение новости"""
    publication_type = 'NE'

class ArticleDetail(BasePostDetail):
    """Детальное отображение статьи"""
    publication_type = 'AR'

# class NewDetail(DetailView):
#     model = Post
#     template_name = 'post.html'
#     context_object_name = 'post'
#
#     def get_object(self, queryset=None):
#         """Проверяем, что объект именно новость"""
#         obj = super().get_object(queryset)
#         if obj.publication_type != 'NE':
#             raise Http404("Это не новость")
#         return obj
#
# class ArticleDetail(DetailView):
#     model = Post
#     template_name = 'post.html'
#     context_object_name = 'post'
#
#     def get_object(self, queryset=None):
#         """Проверяем, что объект именно статья"""
#         obj = super().get_object(queryset)
#         if obj.publication_type != 'AR':
#             raise Http404("Это не статья")
#         return obj


class BasePostCreate(PermissionRequiredMixin, CreateView):
    permission_required = ('news_portal.add_post',)
    form_class = PostForm
    model = Post
    publication_type = None
    base_template = None
    url_namespace = None

    def form_valid(self, form):
        post = form.save(commit=False)
        post.publication_type = self.publication_type
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(f'{self.url_namespace}:detail', kwargs={'pk': self.object.pk})

    def get_template_names(self):
        if self.base_template:
            return [self.base_template]
        return super().get_template_names()

class NewCreate(BasePostCreate):
    publication_type = 'NE'
    base_template = 'new_edit.html'
    url_namespace = 'news'

class ArticleCreate(BasePostCreate):
    publication_type = 'AR'
    base_template = 'article_edit.html'
    url_namespace = 'articles'

# class NewCreate(PermissionRequiredMixin, CreateView):
#     permission_required = ('news_portal.add_post',)
#     form_class = PostForm
#     model = Post
#     template_name = 'new_edit.html'
#
#     def form_valid(self, form):
#         post = form.save(commit=False)
#         post.publication_type = 'NE'
#         return super().form_valid(form)
#
#     def get_success_url(self):
#         return reverse_lazy('news:new_detail', kwargs={'pk': self.object.pk})
#
# class ArticleCreate(PermissionRequiredMixin, CreateView):
#     permission_required = ('news_portal.add_post',)
#     form_class = PostForm
#     model = Post
#     template_name = 'article_edit.html'
#
#     def form_valid(self, form):
#         post = form.save(commit=False)
#         post.publication_type = 'AR'
#         return super().form_valid(form)
#
#     def get_success_url(self):
#         return reverse_lazy('articles:article_detail', kwargs={'pk': self.object.pk})

class BasePostUpdate(PermissionRequiredMixin, UpdateView):
    permission_required = ('news_portal.change_post',)
    form_class = PostForm
    model = Post
    publication_type = None
    error_message = "Запись не соответствует типу"

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if obj.publication_type != self.publication_type:
            raise Http404(self.error_message)
        return obj

# Дочерние классы
class NewUpdate(BasePostUpdate):
    template_name = 'new_edit.html'
    publication_type = 'NE'
    error_message = "Это не новость"

class ArticleUpdate(BasePostUpdate):
    template_name = 'article_edit.html'
    publication_type = 'AR'
    error_message = "Это не статья"

# class NewUpdate(PermissionRequiredMixin, UpdateView):
#     permission_required = ('news_portal.change_post',)
#     form_class = PostForm
#     model = Post
#     template_name = 'new_edit.html'
#
#     def get_object(self, queryset=None):
#         """Проверяем, что объект именно новость"""
#         obj = super().get_object(queryset)
#         if obj.publication_type != 'NE':
#             raise Http404("Это не новость")
#         return obj
#
# class ArticleUpdate(PermissionRequiredMixin, UpdateView):
#     permission_required = ('news_portal.change_post',)
#     form_class = PostForm
#     model = Post
#     template_name = 'article_edit.html'
#
#     def get_object(self, queryset=None):
#         """Проверяем, что объект именно статья"""
#         obj = super().get_object(queryset)
#         if obj.publication_type != 'AR':
#             raise Http404("Это не статья")
#         return obj

class BasePostDelete(DeleteView):
    model = Post
    template_name = 'post_delete.html'
    publication_type = None
    error_message = "Запись не соответствует типу"

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if obj.publication_type != self.publication_type:
            raise Http404(self.error_message)
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['publication_type_name'] = dict(POSITIONS).get(self.object.publication_type, 'неизвестный тип')
        return context

class NewDelete(BasePostDelete):
    publication_type = 'NE'
    success_url = reverse_lazy('news:list')
    error_message = "Это не новость"

class ArticleDelete(BasePostDelete):
    publication_type = 'AR'
    success_url = reverse_lazy('articles:list')
    error_message = "Это не статья"

# class NewDelete(DeleteView):
#     model = Post
#     template_name = 'post_delete.html'
#     success_url = reverse_lazy('news:news_list')
#
#     def get_object(self, queryset=None):
#         """Проверяем, что объект именно новость"""
#         obj = super().get_object(queryset)
#         if obj.publication_type != 'NE':
#             raise Http404("Это не новость")
#         return obj
#
# class ArticleDelete(DeleteView):
#     model = Post
#     template_name = 'post_delete.html'
#     success_url = reverse_lazy('articles:articles_list')
#
#     def get_object(self, queryset=None):
#         """Проверяем, что объект именно статья"""
#         obj = super().get_object(queryset)
#         if obj.publication_type != 'AR':
#             raise Http404("Это не статья")
#         return obj