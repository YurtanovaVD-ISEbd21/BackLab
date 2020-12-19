from django.urls import path

from .views import index, CarView, OrderView, CarList, CarDetail, UserList, UserDetail, OauthVK, VkHook

urlpatterns = [
    path('users/', UserList.as_view()),
    path('users/<int:pk>', UserDetail.as_view()),
    path('cars/', CarList.as_view()),
    path('cars/<int:pk>', CarDetail.as_view()),
    path('orders/', OrderView.as_view()),
    path('oauth/', OauthVK.as_view()),
    path('vk/', VkHook.as_view()),
    path('', index),
]