from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse

from account.models import Profile
from .forms import AdminLoginForm


def admin_login(request):
    if request.user.is_authenticated:
        return redirect('/admin/dashboard/')

    if request.method == 'POST':
        form = AdminLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                messages.info(request, 'Account not found')
                return redirect(reverse('admin_login'))

            user = authenticate(request, username=username, password=password)

            if user and user.is_staff:
                login(request, user)
                return redirect('/admin/dashboard/')

            messages.info(request, 'Invalid password')
            return redirect(reverse('admin_login'))

    else:
        form = AdminLoginForm()

    return render(request, 'management/login_admin.html', {'form': form})

    
@user_passes_test(lambda u: u.is_staff)
def admin_dashboard(request):
    return render(request,
                  'management/admin_dashboard.html')
    
    
@user_passes_test(lambda u: u.is_staff)
def admin_tenants(request):
    all_users = Profile.objects.all().order_by('-id')
    paginator = Paginator(all_users, 2)
    page = request.GET.get('page')
    
    print(f"page: {page}")
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)
    return render(request,
                  'management/admin_tenants.html',
                  {'users' : all_users,
                   'page': posts})
