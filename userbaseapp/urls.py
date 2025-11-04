"""
URL configuration for mymainserver project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# userbaseapp/urls.py
from django.urls import path
from . import views

app_name = 'userbaseapp'

urlpatterns = [
    path('', views.login_view, name='login'),
    path('home/', views.home, name='home'),
    path('logout/', views.logout_view, name='logout'),
    
    # Betting operations
    path('place-bet/', views.place_bet, name='place_bet'),
    path('place-bulk-bet/', views.place_bulk_bet, name='place_bulk_bet'),
    path('load-bets/', views.load_bets, name='load_bets'),
    path('delete-bet/', views.delete_bet, name='delete_bet'),
    
    # Bulk action operations
    path('undo-bulk-action/', views.undo_bulk_action, name='undo_bulk_action'),
    path('get-last-bulk-action/', views.get_last_bulk_action, name='get_last_bulk_action'),
    
    # Summary/Statistics
    path('get-bet-summary/', views.get_bet_summary, name='get_bet_summary'),
]