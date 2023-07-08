from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import UserRegistrationForm,UserUpdateForm,ProfileUpdateForm
from django.contrib.auth.models import User

# Create your views here.
def register(request):
	if request.method=='POST':
		form=UserRegistrationForm(request.POST)
		if form.is_valid():
			form.save()
			username=form.cleaned_data.get('username')
			messages.success(request, f'Account Created for {username}!')
			return redirect('login')	
	else:
		form=UserRegistrationForm()
	return render(request,'users/register.html',{'form':form})

@login_required
def profile(request):
	if request.method == 'POST':
		u_update = UserUpdateForm(request.POST, instance=request.user)
		p_update = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
		
		if u_update.is_valid():
			u_update.save()
			messages.success(request, 'Account Updated!')
			return redirect('profile')
		
		if p_update.is_valid():
			p_update.save()
			messages.success(request, 'Account Updated!')
			return redirect('profile')
	else:
		u_update = UserUpdateForm(instance=request.user)
		p_update = ProfileUpdateForm(instance=request.user.profile)
	
	update_form = {
		'u_update': u_update,
		'p_update': p_update
	}
	
	return render(request, 'users/profile.html', update_form)


def user_list(request):
    users = User.objects.all()
    return render(request, 'users/all_users.html', {'users': users})
