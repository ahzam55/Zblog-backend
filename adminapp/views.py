from django.shortcuts import render
from rest_framework.parsers import JSONParser
from django.http.response import JsonResponse
from adminapp.serializers import *
from adminapp.models import *
from django.views.decorators.csrf import csrf_exempt
import jwt, datetime
from django.contrib.auth import authenticate, login 
from rest_framework.decorators import api_view
from datetime import date
from django.core.paginator import Paginator

# Create your views here.

@csrf_exempt
def signup(request):
    if request.method == "POST":
        try:
            user_data = JSONParser().parse(request)

            password = user_data.get('password')
            print(password)
            username = user_data.get('username')
            print(username)
            email = user_data.get('email')
            print(email)
            role = user_data.get('role')
            print(role)
            contact_no = user_data.get('contact_no')
            print(contact_no)

            if not (password and username and email and role and contact_no):
                return JsonResponse({
                    "hasError": True,
                    "errorCode": 400,
                    "message": "Missing required fields",
                    "debugMessage": "Please provide all required fields"
                }, status=400)

            reg_login = MyUser.objects.create_user(
                username=username,
                email=email,
                password=password,
                contact_no=contact_no,
                role=role
            )
            reg_login.save()

            return JsonResponse({
                "hasError": False,
                "errorCode": 0,
                "message": "Employee registration successful",
                "debugMessage": ""
            }, status=201)

        except Exception as e:
            return JsonResponse({
                "hasError": True,
                "errorCode": 500,
                "message": "Internal Server Error",
                "debugMessage": str(e)
            }, status=500)

    return JsonResponse({
        "hasError": True,
        "errorCode": 405,
        "message": "Invalid request method",
        "debugMessage": "Only POST method is allowed"
    }, status=405)



SECRET_KEY = 'secret'

REFRESH_TOKEN_EXPIRATION = 90  # 1 minute
ACCESS_TOKEN_EXPIRATION = 10  # 1 minute

@csrf_exempt
def signin(request):
    if request.method == "POST":
        user_data = JSONParser().parse(request)
        print(user_data)
        username = user_data.get('username')
        password = user_data.get('password')
        print(username)
        print(password)

        user = authenticate(request, username=username, password=password)

        if user is not None:
            request.session['user_id'] = user.id

            try:
                login_obj = MyUser.objects.get(username=username)

                access_token_payload = {
                    'id': user.id,
                    'role': login_obj.role,  
                    'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRATION),
                    'iat': datetime.datetime.utcnow()
                }

                access_token = jwt.encode(access_token_payload, SECRET_KEY, algorithm='HS256')

                refresh_token_payload = {
                    'id': user.id,
                    'role': login_obj.role,  
                    'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=REFRESH_TOKEN_EXPIRATION),
                    'iat': datetime.datetime.utcnow()
                }

                refresh_token = jwt.encode(refresh_token_payload, SECRET_KEY, algorithm='HS256')

                response_data = {
                    'access_token': access_token,
                    'refresh_token': refresh_token,
                    'user_id': user.id
                }

               
                login(request, user)
                response_data['redirect'] = 'userhome' 

                response = JsonResponse({
                    "hasError": False,
                    "errorCode": 0,
                    "message": "Success",
                    "debugMessage": "",
                    "data": response_data
                })

                
                response.set_cookie(key='access_token', value=access_token, httponly=True)
                response.set_cookie(key='refresh_token', value=refresh_token, httponly=True)

                return response

            except MyUser.DoesNotExist:
                return JsonResponse({
                    "hasError": True,
                    "errorCode": 404,
                    "message": "User does not exist",
                    "debugMessage": ""
                })

        else:
            return JsonResponse({
                "hasError": True,
                "errorCode": 400,
                "message": "Incorrect username or password.",
                "debugMessage": ""
            })

    return JsonResponse({
        "hasError": True,
        "errorCode": 400,
        "message": "Invalid request",
        "debugMessage": ""
    })
    
    
    
SECRET_KEY = 'secret'

REFRESH_TOKEN_EXPIRATION = 90  # 1 minute
ACCESS_TOKEN_EXPIRATION = 1  # 1 minute

@api_view(['POST'])
def refresh_token(request):
    refresh_token = request.data.get('refresh_token', None)

   
    if not refresh_token:
       
        return JsonResponse({"error": "Refresh token is required"}, status=400)

    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=["HS256"])

        user_id = payload['id']
        user = MyUser.objects.get(id=user_id)
      

        access_token_payload = {
            'id': user.id,
            'role': user.role,  
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRATION),
            'iat': datetime.datetime.utcnow()
        }

       
        access_token = jwt.encode(access_token_payload, SECRET_KEY, algorithm='HS256')

        refresh_token_payload = {
            'id': user.id,
            'role': user.role ,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=REFRESH_TOKEN_EXPIRATION),
            'iat': datetime.datetime.utcnow()
        }

        refresh_token = jwt.encode(refresh_token_payload, SECRET_KEY, algorithm='HS256')
        print(10)
        print(refresh_token)
      
        return JsonResponse({
            "access_token": access_token,
            "refresh_token": refresh_token
        })

    except jwt.ExpiredSignatureError:
        return JsonResponse({"error": "Refresh token has expired"}, status=400)
    except jwt.InvalidTokenError:
        return JsonResponse({"error": "Invalid refresh token"}, status=400)
    except MyUser.DoesNotExist:
        return JsonResponse({"error": "User not found"}, status=404)
    
    
    
@csrf_exempt
def blog(request, id=None): 
    if request.method == 'GET':
        status = request.GET.get('status', None)
        title = request.GET.get('title', None)
        page_number = int(request.GET.get('page', 1))  
        page_size = int(request.GET.get('page_size', 2)) 
        user_id = getattr(request, 'user_id', None) 
        

        blogs = BlogPost.objects.filter(author=user_id)

        if status:
            blogs = blogs.filter(status=status)
        if title:
            blogs = blogs.filter(title__icontains=title)
        paginator = Paginator(blogs, page_size)
        page = paginator.get_page(page_number)

        blog_serializer = BlogSerializers(page.object_list, many=True)
    
        return JsonResponse({
            "hasError": False,
            "errorCode": 0,
            "message": "Success",
            "debugMessage": "",
            "data": blog_serializer.data,
            "page": page_number,
            "page_size": page_size,
            "total_pages": paginator.num_pages,
            "total_items": paginator.count
        }, safe=False)

    elif request.method == 'POST':
        blog_data = JSONParser().parse(request)
        print(blog_data)  

        title = blog_data.get('title')
        content = blog_data.get('content')
        status = blog_data.get('status')
        author = getattr(request, 'user_id', None)
        if not title or not content or not status or not author:
            return JsonResponse({
                "hasError": True,
                "errorCode": 400,
                "message": "Missing required fields",
                "debugMessage": "title, content, status, and author are required"
            }, status=400)

        reg_blog = BlogPost()
        reg_blog.title = title
        reg_blog.content = content
        reg_blog.status = status
        reg_blog.created_at = date.today()
        reg_blog.updated_at = date.today()
        reg_blog.author = MyUser.objects.get(id=author)

        reg_blog.save()
        return JsonResponse({
            "hasError": False,
            "errorCode": 0,
            "message": "blog Added Successfully",
            "debugMessage": ""
        }, safe=False)

    elif request.method == 'PUT':
        if id is None:
            return JsonResponse({
                "hasError": True,
                "errorCode": 400,
                "message": "blog ID is required",
                "debugMessage": "Please provide a valid blog ID"
            }, status=400)

        try:
            blog = BlogPost.objects.get(id=id)
            print(id)
        except BlogPost.DoesNotExist:
            return JsonResponse({
                "hasError": True,
                "errorCode": 404,
                "message": "blog not found",
                "debugMessage": f"No blog found with ID {id}"
            }, status=404)

        blog_data = JSONParser().parse(request)
        print(blog_data)

        title = blog_data.get('title')
        content = blog_data.get('content')
        status = blog_data.get('status')
       

        if title:
            blog.title = title
        if content:
            blog.content = content
        if status:
            blog.status = status
            blog.updated_at = date.today()
        blog.save()
        return JsonResponse({
            "hasError": False,
            "errorCode": 0,
            "message": "blog Updated Successfully",
            "debugMessage": ""
        }, safe=False)

    elif request.method == 'DELETE':
        if id is None:
            return JsonResponse({
                "hasError": True,
                "errorCode": 400,
                "message": "blog ID is required",
                "debugMessage": "Please provide a valid blog ID"
            }, status=400)
        try:
            blog = BlogPost.objects.get(id=id)
        except BlogPost.DoesNotExist:
            return JsonResponse({
                "hasError": True,
                "errorCode": 404,
                "message": "blog not found",
                "debugMessage": f"No blog found with ID {id}"
            }, status=404)

        blog.delete()
        return JsonResponse({
            "hasError": False,
            "errorCode": 0,
            "message": "blog Deleted Successfully",
            "debugMessage": ""
        }, safe=False)

    else:
        return JsonResponse({
            "hasError": True,
            "errorCode": 405,
            "message": "Invalid request method",
            "debugMessage": "Only GET, POST, PUT, and DELETE methods are allowed"
        }, status=405)
        
@csrf_exempt
def allblog(request): 
    if request.method == 'GET':
        page = int(request.GET.get('page', 1))
        limit = int(request.GET.get('limit', 5))  

        blog_queryset = BlogPost.objects.filter(status="published")
        paginator = Paginator(blog_queryset, limit)

        try:
            blog_page = paginator.page(page)
        except Exception as e:
            return JsonResponse({
                "hasError": True,
                "errorCode": 1,
                "message": "Error during pagination",
                "debugMessage": str(e),
                "data": []
            })

        blog_serializer = BlogSerializers(blog_page, many=True)

        return JsonResponse({
            "hasError": False,
            "errorCode": 0,
            "message": "Success",
            "debugMessage": "",
            "data": blog_serializer.data,
            "totalCount": paginator.count,  
        }, safe=False)
        
        
@csrf_exempt
def publicblog(request): 
    if request.method == 'GET':
        page = int(request.GET.get('page', 1))
        limit = int(request.GET.get('limit', 5))  

        blog_queryset = BlogPost.objects.filter(status="published")
        paginator = Paginator(blog_queryset, limit)

        try:
            blog_page = paginator.page(page)
        except Exception as e:
            return JsonResponse({
                "hasError": True,
                "errorCode": 1,
                "message": "Error during pagination",
                "debugMessage": str(e),
                "data": []
            })

        blog_serializer = BlogSerializers(blog_page, many=True)

        return JsonResponse({
            "hasError": False,
            "errorCode": 0,
            "message": "Success",
            "debugMessage": "",
            "data": blog_serializer.data,
            "totalCount": paginator.count,  
        }, safe=False)