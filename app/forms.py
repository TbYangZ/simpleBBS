from django import forms
from app.models import Post
from app.models import Messages

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['content']  # 允许用户修改标题和内容


class MessageForm(forms.ModelForm):
    class Meta:
        model = Messages
        fields = ['receiver', 'content']