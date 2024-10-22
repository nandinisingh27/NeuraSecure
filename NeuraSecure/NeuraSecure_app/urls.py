from django.urls import path
from . import views

urlpatterns = [
    path('register/',views.register),
    path('login/',views.login_user),
    path('login_det/',views.login_det),
    path('logout/',views.logout_user),
    path('data_insert/',views.data_insert),
    path('list_data/',views.list_data),
    path('list_cat_data/',views.list_cat_data),
    path('data_status/',views.like_dislike),
    path('list_top/',views.top_categories)
]
