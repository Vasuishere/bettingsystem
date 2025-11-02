from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import CustomUser, Bet
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
import json

def index(request):
    return render(request, 'userbaseapp/index.html')

def login_view(request):
    """Render login form and handle POST authentication."""
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Try direct authenticate (works if username == email)
        user = authenticate(request, username=email, password=password)

        # Fallback: find user by email and authenticate with its username
        if user is None and email:
            user_obj = CustomUser.objects.filter(email__iexact=email).first()
            if user_obj:
                user = authenticate(request, username=user_obj.username, password=password)

        if user is not None:
            auth_login(request, user)
            return redirect('userbaseapp:home')
        else:
            messages.error(request, 'Invalid email or password.')

    return render(request, 'userbaseapp/login.html')

@login_required
def home(request):
    """Home page after successful login"""
    return render(request, 'userbaseapp/home.html')

def logout_view(request):
    auth_logout(request)
    return redirect('userbaseapp:login')

@login_required
@require_http_methods(["POST"])
def place_bet(request):
    """Save a bet to the database"""
    try:
        data = json.loads(request.body.decode('utf-8'))
        number = data.get('number')
        amount = data.get('amount')

        if not number or not amount:
            return JsonResponse({'error': 'Missing number or amount'}, status=400)

        # Validate amount
        amount = float(amount)
        if amount <= 0:
            return JsonResponse({'error': 'Amount must be greater than 0'}, status=400)

        # Save to DB
        bet = Bet.objects.create(
            user=request.user,
            number=str(number),
            amount=amount
        )

        return JsonResponse({
            'success': True,
            'message': 'Bet saved successfully',
            'bet_id': bet.id,
            'user': request.user.username,
            'number': bet.number,
            'amount': str(bet.amount)
        })

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
@require_http_methods(["GET"])
def load_bets(request):
    """Load all bets for the current user"""
    try:
        user_bets = Bet.objects.filter(user=request.user).order_by('-created_at')
        
        # Organize bets by number
        bets_dict = {}
        for bet in user_bets:
            if bet.number not in bets_dict:
                bets_dict[bet.number] = {
                    'total': 0,
                    'history': []
                }
            bets_dict[bet.number]['total'] += float(bet.amount)
            bets_dict[bet.number]['history'].append({
                'id': bet.id,
                'amount': float(bet.amount)
            })
        
        return JsonResponse({
            'success': True,
            'bets': bets_dict
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
@require_http_methods(["POST"])
def delete_bet(request):
    """Delete a specific bet"""
    try:
        data = json.loads(request.body.decode('utf-8'))
        bet_id = data.get('bet_id')

        if not bet_id:
            return JsonResponse({'error': 'Missing bet_id'}, status=400)

        # Find and delete the bet (only if it belongs to the current user)
        bet = Bet.objects.filter(id=bet_id, user=request.user).first()
        
        if not bet:
            return JsonResponse({'error': 'Bet not found or unauthorized'}, status=404)
        
        bet.delete()

        return JsonResponse({
            'success': True,
            'message': 'Bet deleted successfully'
        })

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)