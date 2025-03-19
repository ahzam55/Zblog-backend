from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission

# Create your models here.
class MyUser(AbstractUser):
    role = models.CharField(max_length=50,null=True)
    contact_no = models.CharField(max_length=15) 
    

    groups = models.ManyToManyField(
        Group,
        related_name='myuser_set',  
        blank=True
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='myuser_permissions',  
        blank=True
    )
    
    
class BlogPost(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published')
    ]
    # blog_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    content = models.TextField()
    author = models.ForeignKey(MyUser, on_delete=models.CASCADE, related_name='blog_posts')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    
    def __str__(self):
        return self.title
    
    