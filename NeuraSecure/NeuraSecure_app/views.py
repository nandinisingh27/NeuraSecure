from django.shortcuts import render
from django.http import JsonResponse
import re
from django.utils import timezone
from datetime import datetime
from django.db.models import Count
from django.contrib.auth import authenticate, login, logout
from .models import Data
from .models import Category
from .models import UserLike
from .models import Comment
from django.contrib.auth.models import User
import json

def register(request):
    if request.method=="POST":
        data =json.loads(request.body)
        username = data.get('username')
        if not bool(re.match(r"^[A-Za-z][A-Za-z0-9_]{1,29}$",username)):
            return JsonResponse({'error':'Enter a valid username , Username should contain alphabets and numbers,it should not contain spaces and special characters except underscores'},status =400)
        first_name = data.get('first_name')
        if not bool(re.match(r"^[A-Za-z]{1}[A-Z a-z]{1,15}$",first_name)):
            return JsonResponse({'error':'Enter a valid name, it should not contain numbers'},status =400)
        last_name = data.get('last_name')
        if not bool(re.match(r"^[A-Za-z]{1}[A-Z a-z]{1,10}$",last_name)):
            return JsonResponse({'error':'Enter a valid name, it should not contain numbers'},status =400)
        email = data.get('email')
        if not bool(re.match(r"^[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*@(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?$",email)):
            return JsonResponse({'error':'Please enter a valid email address'},status = 400)
        password = data.get('password')
        cpassword = data.get('cpassword')
        if not bool(re.match(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$",password)):
            return JsonResponse({'error':'password must  contain atleast a special character,a uppercase letter, a lowercase letter,a number and minimum should be of 8 character'},status =400)
        if password != cpassword:
            return JsonResponse({'error':'Password and confirm password do not match'},status = 400)
        if User.objects.filter(username=username).exists():
            return JsonResponse({'error': 'User already exists!!'},status=400)
        User.objects.create_user(username=username, password=password,first_name = first_name,last_name=last_name,email=email)
        return JsonResponse({'message': 'User created'}, status=201)
    else:
        return JsonResponse({'error':'Invalid Method'},status= 405)
    
def login_user(request):
    if request.method=="POST":
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
        if username is None:
            return JsonResponse({'error':'Please enter username'},status=400)
        if password is None:
            return JsonResponse({'error':'Please enter password'},status=400)
        user = authenticate(request , username=username, password=password)
        if user is not None:
            login(request, user)
            username = request.user
            
            return JsonResponse({'message':'User successfully logged in!'}, status=200)
        return JsonResponse({'error': 'Invalid credentials'}, status=401)
    elif request.method == "GET":
        if request.user.is_authenticated:
            return JsonResponse({'is_logged_in': True, 'username': request.user.username}, status=200)
        else:
            return JsonResponse({'is_logged_in': False}, status=200)
    else:
        return JsonResponse({'error':'Invalid method'},status = 405)
    
def login_det(request):
    if request.method =="GET":
        if not request.user.is_authenticated:
            return JsonResponse({'error':'No user is logged in'},status =400)
        user =request.user
        print(user)
        details = User.objects.filter(username = user).values()
        name = details[0]['username']
        return JsonResponse({'user':name},status =200)
    
    
    else:
        return JsonResponse({'error':'Invalid method'},status =405)

    
def logout_user(request):
    if request.method == "POST":
        logout(request)
        return JsonResponse({'message':'Logged out!!'},status = 200)
    else:
        return JsonResponse({'error':'Invalid method'},status =405 )
        

def data_insert(request):
    if request.method=="POST":
        data = json.loads(request.body)
        title = data.get('title')
        if title is None:
            return JsonResponse({'error':'Please enter valid title'},status=400)
        info = data.get('content')
        if info is None:
            return JsonResponse({'error':'Please enter valid information'},status =400)
        if len(info)>6000:
            return JsonResponse({"error":"Data too large to save"},status =400)
        date = timezone.now().strftime("%Y-%m-%d")
        category_list = data.get('category')
        category_ind = category_list[0]
        link = data.get('link')
        if link is None:
            return JsonResponse({'error':'Please provide link also'},status =400)
        if Data.objects.filter(title =title).filter(info =info).exists():
            return JsonResponse({'error':'Data already exists!'},status =400)
        if not Category.objects.filter(name =category_ind).exists():
            category =Category.objects.create(name = category_ind)
            category_details = Category.objects.filter(name = category_ind).values()
            id = category_details[0]['id']
            Data.objects.create(title = title,info =info,category_id = id,link=link,date =date)
        else:
            category_details = Category.objects.filter(name = category_list).values()
            id = category_details[0]['id']
            Data.objects.create(title = title,info =info,category_id = id,link=link,date =date)
        return JsonResponse({'message':'Data inserted successfully'},status=201)
    else:
        return JsonResponse({'error':'Invalid Method'},status =405)
    
    
def list_data(request):
    if request.method == "GET":
        details = Data.objects.all().values()
        id_list=[]
        det=[]
        for item in details:
            val={
                'id':item['id']
            }
            id_list.append(val)
        for item in id_list:
            id = item['id']
            info = Data.objects.filter(id =id).values()
            info_cat_id = info[0]['category_id']
            category_data = Category.objects.filter(id = info_cat_id).values()
            cat_name  = category_data[0]['name']
            val ={
                'id':info[0]['id'],
                'title':info[0]['title'],
                'info':info[0]['info'],
                'category':cat_name,
                'link':info[0]['link'],
                'date':info[0]['date'],
                'likes':info[0]['num_likes']
                }
            det.append(val)
        return JsonResponse({'list':det},status =200)
    else:
        return JsonResponse({'error':'Invalid method'},status =405)
                    
    
def list_cat_data(request):
    if request.method=="GET":
        name = request.GET.get('category')
        print(name)
        category_details = Category.objects.filter(name = name).values()
        id = category_details[0]['id']
        details =[]
        data = Data.objects.filter(category_id = id).values()
        print(data)
        id_list =[]
        for item in data:
            values={
                'id':item['id']
            }
            id_list.append(values)
        print(id_list)
        for i in id_list:
            det= Data.objects.filter(id =i['id']).values()
            print(det)
            for into in det:
                print(into)
                val={
                'title':into['title'],
                'info':into['info'],
                'link':into['link'],
                'date':into['date']
                }
                details.append(val)
        return JsonResponse({'list':details},status =200)
    else:
        return JsonResponse({"error":"Invalid method"},status =405)


def like_dislike(request):
    if request.method == "PATCH":
        user = request.user
        
        if not user.is_authenticated:
            return JsonResponse({'error': 'User not authenticated'}, status=401)

        data = json.loads(request.body)
        post_id = data.get('id')
        comment_content = data.get('comment', None)

        det = Data.objects.filter(id=post_id).first()

        if not det:
            return JsonResponse({'error': 'Post not found'}, status=404)

        user_like = UserLike.objects.filter(user=user, post=det).first()
        message = ''

        if user_like:
            if user_like.is_like:
                user_like.is_like = False
                det.num_likes = max(0, det.num_likes - 1)
                det.num_dislikes += 1
                message = 'Post unliked'
            else:
                user_like.is_like = True
                det.num_dislikes = max(0, det.num_dislikes - 1)
                det.num_likes += 1
                message = 'Post liked'
            user_like.save()
        else:
            UserLike.objects.create(user=user, post=det, is_like=True)
            det.num_likes += 1
            message = 'Post liked'

        if comment_content:
            Comment.objects.create(post=det, user=user, content=comment_content)
            comment_entry = {
                'user': user.username,
                'content': comment_content,
                'created_at': str(datetime.now())
            }
            det.content.append(comment_entry)
            message += f" and comment added: {comment_content}"

        det.save()

        total_likes = det.num_likes - det.num_dislikes

        return JsonResponse({
            'message': message,
            'is_like': user_like.is_like,
            'total_likes': total_likes,
            'comments': det.content
        }, status=200)

    return JsonResponse({'error': 'Invalid method'}, status=405)


def top_categories(request):
    if request.method == "GET":
        categories = Category.objects.annotate(post_count=Count('data')).order_by('-post_count')[:5]

        category_data = [
            {
                'category_id': category.id,
                'category_name': category.name,
                'post_count': category.post_count
            }
            for category in categories
        ]

        return JsonResponse({'top_categories': category_data}, status=200)

    return JsonResponse({'error': 'Invalid method'}, status=405)


