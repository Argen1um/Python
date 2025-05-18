from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.urls import reverse_lazy
from django.contrib.auth.mixins import PermissionRequiredMixin, LoginRequiredMixin
from django.conf import settings

from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView
)
from .models import Post, Category, Author
from .forms import PostForm
from .filters import PostFilter
from pprint import pprint
from .resources import POSITIONS
from django.core.mail import send_mail

@login_required
def subscribe_to_news_category(request, pk):
    category = get_object_or_404(Category, pk=pk)
    category.subscribers.add(request.user)
    send_mail(
        subject=f'Подписка на новости категории {category.name}',
        message=f'Вы подписались на новости категории "{category.name}"',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[request.user.email],
        fail_silently=False
    )
    return redirect('news:list')

@login_required
def unsubscribe_from_news_category(request, pk):
    category = get_object_or_404(Category, pk=pk)
    category.subscribers.remove(request.user)
    send_mail(
        subject=f'Отписка от новостей категории {category.name}',
        message=f'Вы отписались от новостей категории "{category.name}"',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[request.user.email],
        fail_silently=False
    )
    return redirect('news:list')

@login_required
def subscribe_to_articles_category(request, pk):
    category = get_object_or_404(Category, pk=pk)
    category.subscribers.add(request.user)
    send_mail(
        subject=f'Подписка на статьи категории {category.name}',
        message=f'Вы подписались на статьи категории "{category.name}"',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[request.user.email],
        fail_silently=False
    )
    return redirect('articles:list')

@login_required
def unsubscribe_from_articles_category(request, pk):
    category = get_object_or_404(Category, pk=pk)
    category.subscribers.remove(request.user)
    send_mail(
        subject=f'Отписка от статей категории {category.name}',
        message=f'Вы отписались от статей категории "{category.name}"',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[request.user.email],
        fail_silently=False
    )
    return redirect('articles:list')


class NewsCategoryDetailView(DetailView):
    model = Category
    template_name = 'news_category_detail.html'
    context_object_name = 'news_category'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        news = self.object.post_set.filter(publication_type='NE').order_by('-time_in')

        #context['posts'] = news
        #context['page_title'] = f'Новости категории: {self.object.name}'
        context['news'] = news
        return context

class ArticlesCategoryDetailView(DetailView):
    model = Category
    template_name = 'articles_category_detail.html'
    context_object_name = 'articles_category'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        articles = self.object.post_set.filter(publication_type='AR').order_by('-time_in')

        #context['posts'] = articles
        #context['page_title'] = f'Статьи категории: {self.object.name}'
        context['articles'] = articles
        return context

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

class BasePostCreate(PermissionRequiredMixin, CreateView): # LoginRequiredMixin,
    permission_required = ('news_portal.add_post',)
    form_class = PostForm
    model = Post
    publication_type = None
    base_template = None
    url_namespace = None

    def form_valid(self, form):
        post = form.save(commit=False)
        post.publication_type = self.publication_type

        # Получаем или создаем автора для текущего пользователя
        author, created = Author.objects.get_or_create(user=self.request.user)
        post.author = author

        post.save()
        form.save_m2m()  # Сохраняем ManyToMany связи (категории)

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
        # context['publication_type_name'] = dict(POSITIONS).get(self.object.publication_type, 'неизвестный тип')
        return context

class NewDelete(BasePostDelete):
    publication_type = 'NE'
    success_url = reverse_lazy('news:list')
    error_message = "Это не новость"

class ArticleDelete(BasePostDelete):
    publication_type = 'AR'
    success_url = reverse_lazy('articles:list')
    error_message = "Это не статья"
