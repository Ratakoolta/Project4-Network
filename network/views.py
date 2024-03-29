from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.core.paginator import Paginator
import json
from django.http import JsonResponse

from .models import User, Post, Follow, Like

def index(request):
    inicio = Post.objects.all().order_by("id").reverse()

    paginator = Paginator(inicio, 10)
    paginas = request.GET.get('page')
    publicaciones = paginator.get_page(paginas)

    meGustan = Like.objects.all()

    liked = []
    try:
        for like in meGustan:
            if like.user.id == request.user.id:
                liked.append(like.post.id)

    except:
        liked = []

    return render(request, "network/index.html", {
        "inicio": inicio,
        "publicaciones": publicaciones,
        "liked" : liked
    })

def edit(request, post_id):
    if request.method == "POST":
        data = json.loads(request.body)
        edit_post = Post.objects.get(pk=post_id)
        edit_post.post = data["post"]
        edit_post.save()
        return JsonResponse({"message": "Edición exitosa", "data": data["post"]}) 

def profile(request, user_id):
    user = User.objects.get(pk=user_id)
    inicio = Post.objects.filter(user=user).order_by("id").reverse()

    follower = Follow.objects.filter(user=user)
    followed = Follow.objects.filter(followed=user)

    try:
        checkfollow = followed.filter(user=User.objects.get(pk=request.user.id))
        if len(checkfollow) != 0:
            isFollowing = False
        else:
            isFollowing = True
    except:
        isFollowing = False

    paginator = Paginator(inicio, 10)
    paginas = request.GET.get('page')
    publicaciones = paginator.get_page(paginas)

    return render(request, "network/profile.html", {
        "inicio": inicio,
        "publicaciones": publicaciones,
        "username": user.username,
        "follower": follower,
        "followed": followed,
        "isFollowing": isFollowing,
        "user_profile": user
    })

def follow(request):
    userfollow = request.POST['userfollow']
    currentUser = User.objects.get(pk=request.user.id) 
    userfollowData = User.objects.get(username=userfollow)
    f = Follow(user=currentUser, followed=userfollowData) 
    f.save()
    user_id= userfollowData.id
    return HttpResponseRedirect(reverse(profile, kwargs={'user_id': user_id}))

def unfollow(request):
    userfollow = request.POST['userfollow']
    currentUser = User.objects.get(pk=request.user.id)
    userfollowData = User.objects.get(username=userfollow)
    f = Follow.objects.get(user=currentUser, followed=userfollowData) 
    f.delete()
    user_id= userfollowData.id
    return HttpResponseRedirect(reverse(profile, kwargs={'user_id': user_id}))

def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")

def newPost(request):
    if request.method == "POST":
        post = request.POST['post']
        user = User.objects.get(pk=request.user.id)
        post = Post(post=post, user=user)
        post.save()
        return HttpResponseRedirect(reverse(index))

def following(request):
    currentUser = User.objects.get(pk=request.user.id)
    userFollowing = Follow.objects.filter(user=currentUser)
    allPosts = Post.objects.all().order_by('id').reverse()

    siguiendoPosts = []

    for post in allPosts:
        for person in userFollowing:
            if person.followed == post.user:
                siguiendoPosts.append(post)

    paginator = Paginator(siguiendoPosts, 10)
    paginas = request.GET.get('page')
    publicaciones = paginator.get_page(paginas)

    return render(request, "network/following.html", {
        "publicaciones": publicaciones
    })

def remove_like(request, post_id):
    post = Post.objects.get(pk=post_id)
    user = User.objects.get(pk=request.user.id) 
    like = Like.objects.filter(user=user, post=post) 
    like.delete()
    return JsonResponse({"message": "Like removed!"})

def add_like(request, post_id):
    post = Post.objects.get(pk=post_id)
    user = User.objects.get(pk=request.user.id) 
    newLike = Like(user=user, post=post) 
    newLike.save()
    return JsonResponse({"message": "Like added!"})