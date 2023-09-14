from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib import messages
<<<<<<< HEAD
from django.utils.decorators import method_decorator
=======
>>>>>>> b8b7a38f9007bd786575cef10ef0da2b796630b1
from django.views.generic import ListView
from django.urls import reverse
from django.http import JsonResponse

from account.models import Profile
from .forms import AdminLoginForm, PageNumberForm


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
    all_users = Profile.objects.all().order_by('id')
<<<<<<< HEAD
    paginator = Paginator(all_users, 25)

    if request.method == 'POST':
        form = PageNumberForm(request.POST)
        if form.is_valid():
            page = form.cleaned_data['page']
            return redirect('admin_tenants', page=page)
    else:
        form = PageNumberForm()

    page = request.GET.get('page')

=======
    paginator = Paginator(all_users, 3)
    page = request.GET.get('page')
>>>>>>> b8b7a38f9007bd786575cef10ef0da2b796630b1
    try:
        users = paginator.page(page)
    except PageNotAnInteger:
        users = paginator.page(1)
    except EmptyPage:
        users = paginator.page(paginator.num_pages)
<<<<<<< HEAD

    return render(request,
                  'management/admin_tenants.html',
                  {'users': users,
                   'page': page,
                   'page_num': paginator.num_pages,
                   'form': form})

@method_decorator(user_passes_test(lambda u: u.is_staff), name='dispatch')
class TenantsListView(ListView):
    queryset = Profile.objects.all()
    context_object_name = 'users'
    paginate_by = 25
    template_name = 'management/admin_tenants.html'


def toggle_user_active(request, user_id):
    if request.method == 'POST' and request.is_ajax():
        try:
            user = Profile.objects.get(id=user_id)
            user.active = not user.active
            user.save()
            return JsonResponse({'success': True})
        except Profile.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'User not found'})

    return JsonResponse({'success': False, 'error': 'Invalid request'})


=======
    print(f"paginator.num_pages{paginator.num_pages}")
    return render(request,
                  'management/admin_tenants.html',
                  {'users' : users,
                   'page': page,
                   'total_pages': paginator.num_pages})


class TenantsListView(ListView):
    queryset = Profile.objects.all()
    context_object_name = 'users'
    paginate_by = 3
    template_name = 'management/admin_tenants.html'
>>>>>>> b8b7a38f9007bd786575cef10ef0da2b796630b1
