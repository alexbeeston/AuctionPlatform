from django.urls import path

from . import views

app_name = 'auction_app'
urlpatterns = [
	path('', views.login, name='login'),
]