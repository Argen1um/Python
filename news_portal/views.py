from django.http import Http404
from django.shortcuts import render
from django.urls import reverse_lazy
# Импортируем класс, который говорит нам о том,
# что в этом представлении мы будем выводить список объектов из БД
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView
)
from .models import Post
from .forms import PostForm
from .filters import PostFilter
from pprint import pprint

class NewsList(ListView):
    template_name = 'news.html'
    context_object_name = 'posts'
    paginate_by = 10

    def get_queryset(self):
        return Post.objects.filter(publication_type='NE').order_by('-time_in').prefetch_related('categories')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['time_sensation'] = None
        # pprint(context)
        return context

class ArticlesList(ListView):
    template_name = 'articles.html'
    context_object_name = 'posts'
    paginate_by = 10

    def get_queryset(self):
        return Post.objects.filter(publication_type='AR').order_by('-time_in').prefetch_related('categories')

class NewSearch(ListView):
    queryset = (Post.objects\
        .order_by('-time_in')\
        .prefetch_related('categories')
        .filter(publication_type='NE'))
    template_name = 'news_search.html'
    context_object_name = 'posts'
    paginate_by = 10

    # Переопределяем функцию получения списка публикаций
    def get_queryset(self):
        # Получаем обычный запрос
        queryset = super().get_queryset()
        # Используем наш класс фильтрации.
        # self.request.GET содержит объект QueryDict, который мы рассматривали
        # в этом юните ранее.
        # Сохраняем нашу фильтрацию в объекте класса,
        # чтобы потом добавить в контекст и использовать в шаблоне.
        self.filterset = PostFilter(self.request.GET, queryset)
        # Возвращаем из функции отфильтрованный список публикаций
        return self.filterset.qs

    # Метод get_context_data позволяет нам изменить набор данных,
    # который будет передан в шаблон.
    def get_context_data(self, **kwargs):
        # С помощью super() мы обращаемся к родительским классам
        # и вызываем у них метод get_context_data с теми же аргументами,
        # что и были переданы нам.
        # В ответе мы должны получить словарь.
        context = super().get_context_data(**kwargs)
        context['filterset'] = self.filterset
        # pprint(context)
        return context

class NewDetail(DetailView):
    model = Post
    template_name = 'post.html'
    context_object_name = 'post'

    def get_object(self, queryset=None):
        """Проверяем, что объект именно новость"""
        obj = super().get_object(queryset)
        if obj.publication_type != 'NE':
            raise Http404("Это не новость")
        return obj

class ArticleDetail(DetailView):
    model = Post
    template_name = 'post.html'
    context_object_name = 'post'

    def get_object(self, queryset=None):
        """Проверяем, что объект именно статья"""
        obj = super().get_object(queryset)
        if obj.publication_type != 'AR':
            raise Http404("Это не статья")
        return obj

class NewCreate(CreateView):
    form_class = PostForm
    model = Post
    template_name = 'new_edit.html'

    def form_valid(self, form):
        post = form.save(commit=False)
        post.publication_type = 'NE'
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('news:new_detail', kwargs={'pk': self.object.pk})

class ArticleCreate(CreateView):
    form_class = PostForm
    model = Post
    template_name = 'article_edit.html'

    def form_valid(self, form):
        post = form.save(commit=False)
        post.publication_type = 'AR'
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('articles:article_detail', kwargs={'pk': self.object.pk})

class NewUpdate(UpdateView):
    form_class = PostForm
    model = Post
    template_name = 'new_edit.html'

    def get_object(self, queryset=None):
        """Проверяем, что объект именно новость"""
        obj = super().get_object(queryset)
        if obj.publication_type != 'NE':
            raise Http404("Это не новость")
        return obj

class ArticleUpdate(UpdateView):
    form_class = PostForm
    model = Post
    template_name = 'article_edit.html'

    def get_object(self, queryset=None):
        """Проверяем, что объект именно статья"""
        obj = super().get_object(queryset)
        if obj.publication_type != 'AR':
            raise Http404("Это не статья")
        return obj

class NewDelete(DeleteView):
    model = Post
    template_name = 'post_delete.html'
    success_url = reverse_lazy('news:news_list')

    def get_object(self, queryset=None):
        """Проверяем, что объект именно новость"""
        obj = super().get_object(queryset)
        if obj.publication_type != 'NE':
            raise Http404("Это не новость")
        return obj

class ArticleDelete(DeleteView):
    model = Post
    template_name = 'post_delete.html'
    success_url = reverse_lazy('articles:articles_list')

    def get_object(self, queryset=None):
        """Проверяем, что объект именно статья"""
        obj = super().get_object(queryset)
        if obj.publication_type != 'AR':
            raise Http404("Это не статья")
        return obj