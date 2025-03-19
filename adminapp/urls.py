from django.urls import path
from adminapp import views
from adminapp.views import *   






urlpatterns =[

    path('signup/', views.signup, name='signup'),
    path('signin/', views.signin, name='signin'),
    path('api/token/refresh/',refresh_token, name='token_refresh'),
    path('blog/', views.blog, name='blog'),
    path('blog/<id>', views.blog, name='blog'),
    path('blog/<int:id>', views.blog, name='blog'),
    path('allblog/', views.allblog, name='allblog'),
   
  
] 