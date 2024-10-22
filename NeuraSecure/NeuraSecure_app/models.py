from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User


class Category(models.Model):
    name = models.CharField(max_length=255)

class Data(models.Model):
    title = models.CharField(max_length=255, default="Cyber Attack recently occurred")
    info = models.CharField(max_length=1000)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    link = models.CharField(max_length=255)
    date = models.CharField(max_length=50)
    num_likes = models.PositiveIntegerField(default=0)
    num_dislikes = models.PositiveIntegerField(default=0)
    content = models.JSONField(default=list) 
    
    
class UserLike(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL,null=True)
    post = models.ForeignKey(Data, on_delete=models.SET_NULL,null=True)
    is_like = models.BooleanField(default=True)
    
class Comment(models.Model):
    post = models.ForeignKey(Data, on_delete=models.SET_NULL,null=True, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.SET_NULL,null=True)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    
