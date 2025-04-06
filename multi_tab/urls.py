"""Модуль с url"""
from django.urls import path
from .views import (HomeView, MultiplicationView, DivisionView, 
                   ResultsView, SquaresView, NameInputView)

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('name_input/<str:test_type>/', NameInputView.as_view(), name='name_input'),
    path('multiplication/', MultiplicationView.as_view(), name='multiplication'),
    path('division/', DivisionView.as_view(), name='division'),
    path('squares/', SquaresView.as_view(), name='squares'),
    path('results/', ResultsView.as_view(), name='results'),
]
