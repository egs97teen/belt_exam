# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib import messages
import re
import datetime
import dateutil.relativedelta
import bcrypt
from django.db.models import Q

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')


# Create your models here.
class UserManager(models.Manager):
	def register(self, userData):
		messages = []

		for field in userData:
			if len(userData[field]) == 0:
				fields = {
					'name':'Name',
					'username':'Username',
					'password':'Password',
					'confirm_pw':'Confirmation password',
				}
				messages.append(fields[field]+' must be filled in')

		if len(userData['name']) < 3:
			messages.append('First name must be at least three characters long')

		if len(userData['username']) < 3:
			messages.append('Last name must be at least three characters long')

		if all(x.isalpha() or x.isspace() for x in userData['name']):
			pass
		else:
			messages.append('Name must only contain letters')

		try:
			User.objects.get(username=userData['username'])
			messages.append('Username already registered')
		except:
			pass

		try:
			User.objects.get(name=userData['name'])
			messages.append('User already registered under that name')
		except:
			pass

		if len(userData['password']) < 8:
			messages.append('Password must be at least eight characters long')

		if re.search('[0-9]', userData['password']) is None:
			messages.append('Password must contain at least one number')

		if re.search('[A-Z]', userData['password']) is None:
			messages.append('Password must contain at least one capital letter')

		if userData['password'] != userData['confirm_pw']:
			messages.append('Password and confirmation password must match')

		if len(messages) > 0:
			return messages
		else:
			hashed_pw = bcrypt.hashpw(userData['password'].encode(), bcrypt.gensalt())
			new_user = User.objects.create(name=userData['name'], username=userData['username'], hashed_pw=hashed_pw)
			return new_user.id

	def login(self, userData):
		messages = []

		for field in userData:
			if len(userData[field]) == 0:
				fields = {
					'login_username':'Username',
					'login_password':'Password'
				}
				messages.append(fields[field]+' must be filled in')

		try:
			user = User.objects.get(username=userData['login_username'])
			encrypted_pw = bcrypt.hashpw(userData['login_password'].encode(), user.hashed_pw.encode())
			if encrypted_pw == user.hashed_pw:
				return user.id
			else:
				messages.append('Wrong password')
		except:
			messages.append('User not registered')

		if len(messages) > 0:
			return messages

class TripManager(models.Manager):
	def add_trip(self, userData, user_id):
		messages = []

		for field in userData:
			if len(userData[field]) == 0:
				fields = {
					'destination':'Destination',
					'description':'Description',
					'start_date':'Travel Date From',
					'end_date':'Travel Date To'
				}
				messages.append(fields[field]+' must be filled in')

		if userData['start_date']:
			start = datetime.datetime.strptime(userData['start_date'], "%Y-%m-%d")
			now = datetime.datetime.now()

			if start <= now:
				messages.append('Pick a date in the future')

		if userData['end_date']:
			start = datetime.datetime.strptime(userData['start_date'], "%Y-%m-%d").date()
			end = datetime.datetime.strptime(userData['end_date'], "%Y-%m-%d").date()

			if end < start:
				messages.append('Date of Travel From must be after or the same day as date of Travel To')

		user = User.objects.get(id=user_id)

		if userData['start_date'] and userData['end_date']:
			start = datetime.datetime.strptime(userData['start_date'], "%Y-%m-%d").date()
			end = datetime.datetime.strptime(userData['end_date'], "%Y-%m-%d").date()

			user_trips = Trip.objects.filter(Q(traveler=user) | Q(planner=user))
			for trip in user_trips:
				if start >= trip.start_date and start <= trip.end_date:
					messages.append('You already have a trip planned at this time')
					break
				elif end >= trip.start_date and end <= trip.end_date:
					messages.append('You already have a trip planned at this time')
					break

		if len(messages) > 0:
			return messages
		else:
			new_trip = Trip.objects.create(destination=userData['destination'], start_date=userData['start_date'], end_date=userData['end_date'], planner=user, plan=userData['description'])
			return new_trip.id

	def join_trip(self, trip_id, user_id):
		messages = []
		join_trip = Trip.objects.get(id=trip_id)
		join_start = join_trip.start_date
		join_end = join_trip.end_date

		user = User.objects.get(id=user_id)
		user_trips = Trip.objects.filter(Q(traveler__id=user.id) | Q(planner__id=user.id))

		for trip in user_trips:
			if join_start >= trip.start_date and join_start <= trip.end_date:
				messages.append('You already have a trip planned at this time')
				break
			elif join_end >= trip.start_date and join_end <= trip.end_date:
				messages.append('You already have a trip planned at this time')
				break

		if len(messages) > 0:
			return messages
		else:
			join_success = join_trip.traveler.add(user)
			return join_success

class User(models.Model):
	name = models.CharField(max_length=255)
	username = models.CharField(max_length=255)
	hashed_pw = models.CharField(max_length=255)
	created_at = models.DateField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
	objects = UserManager()

class Trip(models.Model):
	destination = models.CharField(max_length=255)
	start_date = models.DateField()
	end_date = models.DateField()
	traveler = models.ManyToManyField(User, related_name='travel_destination')
	planner = models.ForeignKey(User)
	plan = models.TextField(max_length=1000)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
	objects = TripManager()