from django import forms
from django.forms import Textarea
from django.utils.translation import gettext_lazy as _

from .models import Comment, Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group', 'image')
        labels = {
            'text': _('Текст поста'),
            'group': _('Группа')
        }
        help_texts = {
            'text': _('Текст нового поста'),
            'group': _('Группа, к которой будет относиться пост')
        }
        widgets = {
            'text': Textarea(attrs={'cols': 40, 'rows': 10}),
        }

    def clean_text(self):
        text = self.cleaned_data['text']
        if len(text) == 0:
            raise forms.ValidationError('Вам нужно написать что-нибудь!')
        return text


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)

    def clean_text(self):
        text = self.cleaned_data['text']
        if len(text) == 0:
            raise forms.ValidationError('Вам нужно написать что-нибудь!')
        return text
