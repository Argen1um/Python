from django import forms
from django.core.exceptions import ValidationError

from .models import Post

class PostForm(forms.ModelForm):
    headline = forms.CharField(max_length=255)

    class Meta:
        model = Post
        fields = [
#            'author',
#            'publication_type',
#            'time_in',
            'categories',
            'headline',
            'text',
            'rating',
        ]
        widgets = {
            'categories': forms.CheckboxSelectMultiple(),
        }

    def clean(self):
        cleaned_data = super().clean()
        headline = cleaned_data.get("headline")
        text = cleaned_data.get("text")
        if text == headline:
            raise ValidationError(
                "Заголовок не должно быть идентичным тексту"
            )
        return cleaned_data
