# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, redirect
from .models import User
from django.contrib import messages
from django.core.urlresolvers import reverse

# Create your views here.
def index(request):
	if 'user' in request.session:
		return redirect(reverse('home'))
	else:
		return render(request, 'belt_exam_app/index.html')

def login(request):
	if request.method == 'POST':
		login = User.objects.login(request.POST.copy())
		if isinstance(login, list):
			for item in login:
				messages.error(request, item)
			return redirect(reverse('index'))
		else:
			request.session['user'] = login.id
			return redirect(reverse('home'))
	else:
		return redirect(reverse('index'))

def register(request):
	if request.method == 'POST':
		register = User.objects.register(request.POST.copy())
		if isinstance(register, list):
			for item in register:
				messages.error(request, item)
			return redirect(reverse('index'))
		else:
			request.session['user'] = register.id
			return redirect(reverse('home'))
	else:
		return redirect(reverse('index'))

def home(request):
	if 'user' in request.session:
		user = User.objects.get(id = request.session['user'])
		context = {
			'name':user.first_name
		}
		return render(request, 'belt_exam_app/home.html', context)
	else:
		messages.error(request, 'Log in or register first')
		return redirect(reverse('index'))

def logout(request):
	request.session.pop('user')
	return redirect(reverse('index'))