# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib import messages
import re
import datetime
import dateutil.relativedelta
import bcrypt

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')

# Create your models here.
class UserManager(models.Manager):
	def register(self, userData):
		messages = []

		for field in userData:
			if len(userData[field]) == 0:
				fields = {
					'first_name':'First name',
					'last_name':'Last name',
					'email':'Email',
					'password':'Password',
					'confirm_pw':'Confirmation password',
					'birthday':'Birthday'
				}
				messages.append(fields[field]+' must be filled in')

		if len(userData['first_name']) < 2:
			messages.append('First name must be at least two characters long')

		if len(userData['last_name']) < 2:
			messages.append('Last name must be at least two characters long')

		if userData['first_name'].isalpha() == False or userData['last_name'].isalpha() == False:
			messages.append('Name must only contain letters')

		if not EMAIL_REGEX.match(userData['email']):
			messages.append('Must enter a valid email')

		try:
			User.objects.get(email=userData['email'])
			messages.append('Email already registered')
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

		if userData['birthday']:
			birthday = datetime.datetime.strptime(userData['birthday'], '%Y-%m-%d')
			now = datetime.datetime.now()
			age = dateutil.relativedelta.relativedelta(now, birthday)

			if birthday > now:
				messages.append('Pick a date in the past')
			if age.years < 18:
				messages.append('Must be at least 18 years old to register')

		if len(messages) > 0:
			return messages
		else:
			hashed_pw = bcrypt.hashpw(userData['password'].encode(), bcrypt.gensalt())
			new_user = User.objects.create(first_name=userData['first_name'], last_name=userData['last_name'], email=userData['email'], hashed_pw=hashed_pw, birthday=userData['birthday'])
			return new_user

	def login(self, userData):
		messages = []

		for field in userData:
			if len(userData[field]) == 0:
				fields = {
					'login_email':'Email',
					'login_password':'Password'
				}
				messages.append(fields[field]+' must be filled in')

		try:
			user = User.objects.get(email=userData['login_email'])
			encrypted_pw = bcrypt.hashpw(userData['login_password'].encode(), user.hashed_pw.encode())
			if encrypted_pw == user.hashed_pw:
				return user
			else:
				messages.append('Wrong password')
		except:
			messages.append('User not registered')

		if len(messages) > 0:
			return messages

class User(models.Model):
	first_name = models.CharField(max_length=255)
	last_name = models.CharField(max_length=255)
	email = models.CharField(max_length=255)
	hashed_pw = models.CharField(max_length=255)
	birthday = models.DateField()
	created_at = models.DateField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
	objects = UserManager()