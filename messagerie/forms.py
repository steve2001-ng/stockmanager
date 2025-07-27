from django import forms
from django.contrib.auth import get_user_model
from .models import Message, Comment

User = get_user_model()

class MessageForm(forms.ModelForm):
    mentions = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        required=False,
        widget=forms.SelectMultiple(attrs={
            'class': 'form-select',
            'size': 5
        })
    )

    class Meta:
        model = Message
        fields = ['subject', 'body', 'mentions']
        widgets = {
            'subject': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Objet du message…'
            }),
            'body': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Votre message…',
                'rows': 5
            }),
        }

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['body']
        widgets = {
            'body': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Écrire un commentaire…',
                'rows': 2
            }),
        }
