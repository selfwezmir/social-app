from django.http import HttpResponse,JsonResponse
from django.shortcuts import render, redirect, get_list_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib.auth.models import User
from django.contrib import messages
from .forms import LoginForm
from post.models import Post
from post.forms import PostForm
from .models import Profile, Follower
from django.apps import apps


def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(request,
                                username=cd['username'],
                                password=cd['password'])
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return HttpResponse('Authenticated successfully')
                else:
                    return HttpResponse('Disabled account')
            else:
                return HttpResponse('Invalid login')
    else:
        form = LoginForm()
    return render(request, 'account/login.html', {'form': form})


@login_required
def dashboard(request):
    posts = Post.objects.all().filter()
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            new_post = form.save(commit=False)
            new_post.author = request.user
            new_post.save()
            return redirect('dashboard')
    else:
        form = PostForm()
    return render(request,
                  'account/dashboard.html',
                  {'section': 'dashboard', 'posts': posts, 'form': form})


@login_required
def people_list(request):
    peoples = Profile.objects.all().exclude(user=request.user)
    return render(request,
                  'account/people.html',
                  {'section': 'people', 'peoples': peoples})


@login_required
def market_list(request):
    return render(request,
                  'account/market.html',
                  {'section': 'market'})


@login_required
def my_profile(request, id):
    posts = Post.objects.all().filter(author=id)
    # if posts:
    #     user_post = posts[0].author.profile.photo.url
    # else:
    user_post = User.objects.get(id=id)
    test = user_post.following.count
    following = 2
    return render(request,
                  'account/profile_page.html',
                  {'section': 'my_profile', 'posts': posts, 'user_post': user_post, 'followers': test, 'following': following})


@require_POST
@login_required
def user_follow(request):
    user_id = request.POST.get('id')
    action = request.POST.get('action')
    if user_id and action:
        try:
            user = User.objects.get(id=user_id)
            if action == 'follow':
                Follower.objects.get_or_create(user_from=request.user, user_to=user)
            else:
                Follower.objects.filter(user_from=request.user, user_to=user).delete()
            return JsonResponse({'status': 'ok'})
        except User.DoesNotExist:
            return JsonResponse({'status': 'error'})
    return JsonResponse({'status': 'error'})
