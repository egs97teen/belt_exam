# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, redirect
from .models import User, Trip
from django.db.models import Q
from django.contrib import messages
from django.core.urlresolvers import reverse

# Create your views here.
def index(request):
	if 'user' in request.session:
		return redirect(reverse('travels'))
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
			request.session['user'] = login
			return redirect(reverse('travels'))
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
			request.session['user'] = register
			return redirect(reverse('travels'))
	else:
		return redirect(reverse('index'))

def travels(request):
	if 'user' in request.session:
		user = User.objects.get(id = request.session['user'])
		user_name = user.name.split()
		user_trips = Trip.objects.filter(Q(traveler__id=user.id) | Q(planner__id=user.id)).order_by('start_date')
		other_trips = Trip.objects.exclude(traveler__id=user.id).exclude(planner__id=user.id).order_by('start_date')
		context = {
			'name':user_name[0],
			'user_trips':user_trips,
			'other_trips':other_trips
		}
		return render(request, 'belt_exam_app/travels.html', context)
	else:
		messages.error(request, 'Log in or register first')
		return redirect(reverse('index'))

def add_travel(request):
	return render(request, 'belt_exam_app/add_travel.html')

def add_trip(request):
	if request.method == 'POST':
		trip = Trip.objects.add_trip(request.POST.copy(), request.session['user'])
		if isinstance(trip, list):
			for item in trip:
				messages.error(request, item)
			return redirect(reverse('add_travel'))
		else:
			return redirect(reverse('travels'))

def trip(request, trip_id):
	trip = Trip.objects.get(id=trip_id)
	travelers = User.objects.filter(travel_destination=trip)
	context = {
		'trip':trip,
		'travelers':travelers
	}
	return render(request, 'belt_exam_app/trip.html', context)

def join(request, trip_id):
	trip = Trip.objects.get(id=trip_id)
	join_trip = Trip.objects.join_trip(trip.id, request.session['user'])
	if isinstance(join_trip, list):
		for item in join_trip:
			messages.error(request, item)
		return redirect(reverse('travels'))
	else:
		return redirect(reverse('travels'))

def logout(request):
	request.session.pop('user')
	return redirect(reverse('index'))