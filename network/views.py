from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from datetime import datetime
import json
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from django.http import JsonResponse




from .models import User, Post, Like, Follow


def index(request):
    # If form submitted
    if request.method == "POST":
        # Capture input from post form
        user = request.user
        post = request.POST["post"]
        timestamp = datetime.now()
        # Check - Proceed only if post is not empty
        if post != "":
            Post.objects.create(user=user, post=post, timestamp=timestamp, likes=0)
    # Collect all posts within Post model and show in reverse chronological order (most recent first)
    posts = Post.objects.all().order_by('-timestamp')
    
    for post in posts:
        post.likes = Like.objects.filter(post=post.id).count()
        post.save()
    
    # Using Paginator in a view function
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, "network/index.html", {
        "page_obj": page_obj # most recent post first
    })


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


def profile(request, username):
    username = User.objects.get(id=username)
    # Set button to "Follow" if not following
    button = "Follow" if Follow.objects.filter(follower=request.user, following=username).count() == 0 else "Unfollow"

    if request.method == "POST":
        if request.POST["button"] == "Follow":
            button = "Unfollow"
            Follow.objects.create(follower=request.user, following=username)
        else:
            button = "Follow"
            Follow.objects.get(follower=request.user, following=username).delete()
    
    posts = Post.objects.filter(user=username.id).order_by('-timestamp')
    for post in posts:
        post.likes = Like.objects.filter(post=post.id).count()
        post.save()

    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)


    return render(request, "network/profile.html", {
        "username": username,
        "followers": Follow.objects.filter(following=username).count(),
        "following": Follow.objects.filter(follower=username).count(),
        "page_obj": page_obj,
        "button": button
    })


def following(request):
    user = request.user
    # filter only for user IDs that current user is following
    following = Follow.objects.filter(follower=request.user).values('following_id')
    # collect posts that are only from user IDs from following and order by reverse chronological order (most recent first)
    posts = Post.objects.filter(user__in=following).order_by('-timestamp')
    
    for post in posts:
        post.likes = Like.objects.filter(post=post.id).count()
        post.save()
    
    # Using Paginator in a view function
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, "network/following.html", {
        "page_obj": page_obj # most recent post first
    })

@csrf_exempt
def edit(request, post_id):
    post = Post.objects.get(id=post_id)

    if request.method == "PUT":
        data = json.loads(request.body)
        if data.get("post") is not None:
            post.post = data["post"]
        post.save()
        return HttpResponse(status=204)


@csrf_exempt
def like(request, post_id):
    post = Post.objects.get(id=post_id)
    # Return post likes
    if request.method == "GET":
        return JsonResponse(post.serialize())
    # Update whether like or unlike
    if request.method == "PUT":
        data = json.loads(request.body)
        print(data.get("like"))
        if data.get("like"):
            Like.objects.create(user=request.user, post=post)
            post.likes = Like.objects.filter(post=post).count()
        else: # unlike
            Like.objects.filter(user=request.user, post=post).delete()
            post.likes = Like.objects.filter(post=post).count()
        post.save()
        return HttpResponse(status=204)