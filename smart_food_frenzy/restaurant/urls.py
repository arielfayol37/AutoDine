from django.urls import path
from . import views

app_name = 'restaurant'

urlpatterns = [
    path('check_feasible_items/', views.check_feasible_items, name='check_feasible_items'),
    path("order_items/", views.order_items, name="order items"),
    path('sse/', views.sse_view, name='sse'),
    path('menu/', views.menu_view, name='menu'),
    path("ingredients_list", views.ingredients_list, name='ingredients_list'),
    path('llm_thinking/<str:set_thinking>', views.llm_thinking, name="llm_thinking"),
    path('llm_recording/<str:set_recording>', views.llm_recording, name="llm_recording")
]