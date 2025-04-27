from django.db import models
from django.db.models import Sum
from django.contrib.auth.models import User
from .resources import POSITIONS

class Author(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    rating = models.IntegerField(default=0)

    def update_rating(self):
        post_rating = Post.objects.filter(author=self).aggregate(total=Sum('rating'))['total'] or 0
        comment_rating =Comment.objects.filter(user=self.user).aggregate(total=Sum('rating'))['total'] or 0
        post_comment_rating = Comment.objects.filter(post__author=self).aggregate(total=Sum('rating'))['total'] or 0
        self.rating = post_rating * 3 + comment_rating + post_comment_rating
        self.save()

class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)
    def __str__(self):
        return self.name.title()

class Post(models.Model):
    author = models.ForeignKey(Author, on_delete = models.CASCADE)
    publication_type = models.CharField(max_length=2, choices=POSITIONS, default='NE')
    time_in = models.DateTimeField(auto_now_add=True)
    categories = models.ManyToManyField(Category, through = 'PostCategory')
    headline = models.CharField(max_length=255)
    text = models.TextField()
    rating = models.IntegerField(default=0)

    def __str__(self):
        return f'{self.headline.title()}: {self.text[:20]}'

    def preview(self):
        return self.text[:124] + '...'

    def like(self):
        self.rating += 1
        self.save()

    def dislike(self):
        if self.rating:
            self.rating -= 1
            self.save()

class PostCategory(models.Model):
    post = models.ForeignKey(Post, on_delete = models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete = models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.CharField(max_length=255)
    time_in = models.DateTimeField(auto_now_add=True)
    rating = models.IntegerField(default=0)

    def like(self):
        self.rating += 1
        self.save()

    def dislike(self):
        if self.rating:
            self.rating -= 1
            self.save()