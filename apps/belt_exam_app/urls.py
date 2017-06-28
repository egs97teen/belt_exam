from django.conf.urls import url
from . import views

urlpatterns = [
  url(r'^$', views.index, name="index"),
  url(r'register$', views.register, name="register"),
  url(r'login$', views.login, name="login"),
  url(r'logout$', views.logout, name="logout"),
  url(r'travels$', views.travels, name="travels"),
  url(r'travels/add$', views.add_travel, name="add_travel"),
  url(r'add_trip$', views.add_trip, name="add_trip"),
  url(r'travels/destination/(?P<trip_id>\d+)$', views.trip, name="trip"),
  url(r'join/(?P<trip_id>\d+)$', views.join, name="join")
  ]