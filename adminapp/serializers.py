from rest_framework import serializers
from adminapp.models import *


class MyUserSerializer(serializers.ModelSerializer):
    position_title = serializers.CharField(source='position.post_name', read_only=True)  
    
    class Meta:
        model = MyUser
        fields = ['username', 'contact_no', 'email']
        
class BlogSerializers(serializers.ModelSerializer):
    author_username = serializers.CharField(source='author.username', read_only=True)

    class Meta:
        model = BlogPost
        fields = '__all__'