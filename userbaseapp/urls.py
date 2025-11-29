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
    path('home/', views.home, name='home'),
    path('logout/', views.logout_view, name='logout'),
    path('master-delete-all-bets/', views.master_delete_all_bets, name='master_delete_all_bets'),
    path('get-total-bet-count/', views.get_total_bet_count, name='get_total_bet_count'),
    
    # Betting operations
    path('place-bet/', views.place_bet, name='place_bet'),
    path('place-bulk-bet/', views.place_bulk_bet, name='place_bulk_bet'),
    path('load-bets/', views.load_bets, name='load_bets'),
    path('delete-bet/', views.delete_bet, name='delete_bet'),
    
    # Bulk action operations
    path('undo-bulk-action/', views.undo_bulk_action, name='undo_bulk_action'),
    path('get-last-bulk-action/', views.get_last_bulk_action, name='get_last_bulk_action'),
    
    # Motar and Comman Pana operations
    path('generate-motar-numbers/', views.generate_motar_numbers, name='generate_motar_numbers'),
    path('find-comman-pana-numbers/', views.find_comman_pana_numbers, name='find_comman_pana_numbers'),
    path('place-motar-bet/', views.place_motar_bet, name='place_motar_bet'),
    path('place-comman-pana-bet/', views.place_comman_pana_bet, name='place_comman_pana_bet'),
    path('place-set-pana-bet/', views.place_set_pana_bet, name='place_set_pana_bet'),
    path('place-group-bet/', views.place_group_bet, name='place_group_bet'),
    
    # Summary/Statistics
    path('get-bet-summary/', views.get_bet_summary, name='get_bet_summary'),
    path('get-bet-total/', views.get_bet_total, name='get_bet_total'),
    path('get-all-bet-totals/', views.get_all_bet_totals, name='get_all_bet_totals'),
    path('get-bulk-action-history/', views.get_bulk_action_history, name='get_bulk_action_history'),
    
    # Database storage info
    path('get-database-storage/', views.get_database_storage, name='get_database_storage'),
    
    # Column betting
    path('place-column-bet/', views.place_column_bet, name='place_column_bet'),
    path('get-column-totals/', views.get_column_totals, name='get_column_totals'),
]