# userbaseapp/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import CustomUser, Bet, BulkBetAction
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.db import transaction
from django.db.models import Sum
from decimal import Decimal
import json


# Jodi Vagar number mappings
JODI_VAGAR_NUMBERS = {
    1: [137, 146, 470, 579, 380, 119, 155, 227, 335, 399, 588, 669],
    2: [147, 246, 480, 138, 570, 228, 255, 336, 499, 688, 660, 200],
    3: [139, 148, 157, 247, 580, 166, 229, 300, 337, 377, 599, 779],
    4: [149, 248, 680, 257, 158, 220, 266, 338, 446, 699, 770, 400],
    5: [159, 258, 357, 168, 249, 113, 177, 339, 366, 447, 799, 500],
    6: [169, 268, 240, 358, 259, 114, 277, 330, 448, 466, 880, 600],
    7: [179, 359, 250, 269, 368, 115, 133, 188, 377, 449, 557, 700],
    8: [279, 260, 350, 369, 468, 116, 224, 288, 440, 477, 558, 800],
    9: [379, 270, 469, 450, 360, 117, 144, 199, 225, 388, 559, 577],
    10: [136, 280, 460, 370, 479, 118, 226, 244, 299, 488, 550, 668]
}

DADAR_NUMBERS = [678, 345, 120, 789, 456, 123, 890, 567, 234, 190]

# Eki/Beki number mappings
EKI_BEKI_NUMBERS = {
    'EKI': [137, 135, 139, 157, 159, 179, 357, 359, 379, 579],
    'BEKI': [246, 248, 240, 268, 260, 280, 468, 460, 480, 680]
}

ALL_COLUMN_DATA = [
    [128, 137, 146, 236, 245, 290, 380, 470, 489, 560, 579, 678, 100, 119, 155, 227, 335, 344, 399, 588, 669, 777],
    [129, 138, 147, 156, 237, 246, 345, 390, 480, 570, 589, 679, 110, 200, 228, 255, 336, 499, 660, 688, 778, 444],
    [120, 139, 148, 157, 238, 247, 256, 346, 490, 580, 670, 689, 166, 229, 300, 337, 355, 445, 599, 779, 788, 111],
    [130, 149, 158, 167, 239, 248, 257, 347, 356, 590, 680, 789, 112, 220, 266, 338, 400, 446, 455, 699, 770, 888],
    [140, 159, 168, 230, 249, 258, 267, 348, 357, 456, 690, 780, 113, 122, 177, 339, 366, 447, 500, 799, 889, 555],
    [123, 150, 169, 178, 240, 259, 268, 349, 358, 367, 457, 790, 114, 277, 330, 448, 466, 556, 600, 880, 899, 222],
    [124, 160, 179, 250, 269, 278, 340, 359, 368, 458, 467, 890, 115, 133, 188, 223, 377, 449, 557, 566, 700, 999],
    [125, 134, 170, 189, 260, 279, 350, 369, 378, 459, 468, 567, 116, 224, 233, 288, 440, 477, 558, 800, 990, 666],
    [126, 135, 180, 234, 270, 289, 360, 379, 450, 469, 478, 568, 117, 144, 199, 225, 388, 559, 577, 667, 900, 333],
    [127, 136, 145, 190, 235, 280, 370, 389, 460, 479, 559, 578, 118, 226, 244, 299, 334, 488, 550, 668, 677, '000']
]


def get_sp_numbers():
    """Get all SP numbers (first 12 rows, 120 numbers)"""
    sp_numbers = []
    for col in ALL_COLUMN_DATA:
        sp_numbers.extend([str(num) for num in col[0:12]])
    return sp_numbers


def get_dp_numbers():
    """Get all DP numbers (rows 13-22, 100 numbers)"""
    dp_numbers = []
    for col in ALL_COLUMN_DATA:
        dp_numbers.extend([str(num) for num in col[12:22]])
    return dp_numbers


def get_dadar_numbers():
    """Get all Dadar numbers (10 numbers)"""
    return [str(num) for num in DADAR_NUMBERS]


def get_eki_beki_numbers(bet_type):
    """Get Eki or Beki numbers"""
    return [str(num) for num in EKI_BEKI_NUMBERS.get(bet_type, [])]


def index(request):
    return render(request, 'userbaseapp/index.html')


def login_view(request):
    """Render login form and handle POST authentication."""
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = authenticate(request, username=email, password=password)

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
    """Save a single bet to the database"""
    try:
        data = json.loads(request.body.decode('utf-8'))
        number = data.get('number')
        amount = data.get('amount')

        if not number or not amount:
            return JsonResponse({'error': 'Missing number or amount'}, status=400)

        amount = Decimal(str(amount))
        if amount <= 0:
            return JsonResponse({'error': 'Amount must be greater than 0'}, status=400)

        bet = Bet.objects.create(
            user=request.user,
            number=str(number),
            amount=amount
        )

        return JsonResponse({
            'success': True,
            'message': 'Bet saved successfully',
            'bet_id': bet.id,
            'number': bet.number,
            'amount': str(bet.amount)
        })

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_http_methods(["POST"])
@transaction.atomic
def place_bulk_bet(request):
    """Place bulk bets (SP, DP, Jodi Vagar, Dadar, Eki, or Beki)"""
    try:
        data = json.loads(request.body.decode('utf-8'))
        bet_type = data.get('type')  # 'SP', 'DP', 'JODI', 'DADAR', 'EKI', or 'BEKI'
        amount = data.get('amount')

        if not bet_type or not amount:
            return JsonResponse({'error': 'Missing type or amount'}, status=400)

        amount = Decimal(str(amount))
        if amount <= 0:
            return JsonResponse({'error': 'Amount must be greater than 0'}, status=400)

        # Determine which numbers to bet on
        if bet_type == 'SP':
            numbers = get_sp_numbers()
        elif bet_type == 'DP':
            numbers = get_dp_numbers()
        elif bet_type == 'JODI':
            column = data.get('column')
            jodi_type = data.get('jodi_type')  # 5, 7, or 12
            
            if not column or not jodi_type:
                return JsonResponse({'error': 'Missing column or jodi_type'}, status=400)
            
            column = int(column)
            jodi_type = int(jodi_type)
            
            if column not in JODI_VAGAR_NUMBERS:
                return JsonResponse({'error': 'Invalid column'}, status=400)
            
            all_jodi_numbers = JODI_VAGAR_NUMBERS[column]
            
            if jodi_type == 5:
                numbers = [str(n) for n in all_jodi_numbers[:5]]
            elif jodi_type == 7:
                numbers = [str(n) for n in all_jodi_numbers[-7:]]
            elif jodi_type == 12:
                numbers = [str(n) for n in all_jodi_numbers]
            else:
                return JsonResponse({'error': 'Invalid jodi_type'}, status=400)
        elif bet_type == 'DADAR':
            numbers = get_dadar_numbers()
        elif bet_type in ['EKI', 'BEKI']:
            numbers = get_eki_beki_numbers(bet_type)
        else:
            return JsonResponse({'error': 'Invalid bet type'}, status=400)

        # Create bulk action record
        bulk_action = BulkBetAction.objects.create(
            user=request.user,
            action_type=bet_type,
            amount=amount,
            total_bets=len(numbers),
            jodi_column=data.get('column') if bet_type == 'JODI' else None,
            jodi_type=data.get('jodi_type') if bet_type == 'JODI' else None
        )

        # Create all bets
        bets_created = []
        for number in numbers:
            bet = Bet.objects.create(
                user=request.user,
                number=str(number),
                amount=amount,
                bulk_action=bulk_action
            )
            bets_created.append({
                'id': bet.id,
                'number': bet.number,
                'amount': str(bet.amount)
            })

        return JsonResponse({
            'success': True,
            'message': f'{len(numbers)} bets placed successfully',
            'bulk_action_id': bulk_action.id,
            'total_bets': len(numbers),
            'bets': bets_created
        })

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_http_methods(["GET"])
def load_bets(request):
    """Load all bets for the current user organized by number"""
    try:
        user_bets = Bet.objects.filter(user=request.user).order_by('-created_at')
        
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
                'amount': float(bet.amount),
                'created_at': bet.created_at.strftime('%Y-%m-%d %H:%M:%S')
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


@login_required
@require_http_methods(["POST"])
def undo_bulk_action(request):
    """Undo the last bulk betting action"""
    try:
        data = json.loads(request.body.decode('utf-8'))
        bulk_action_id = data.get('bulk_action_id')

        if not bulk_action_id:
            return JsonResponse({'error': 'Missing bulk_action_id'}, status=400)

        bulk_action = BulkBetAction.objects.filter(
            id=bulk_action_id, 
            user=request.user,
            is_undone=False
        ).first()
        
        if not bulk_action:
            return JsonResponse({'error': 'Bulk action not found or already undone'}, status=404)
        
        success, message = bulk_action.undo()

        return JsonResponse({
            'success': success,
            'message': message
        })

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_http_methods(["GET"])
def get_last_bulk_action(request):
    """Get the last bulk action for undo button visibility"""
    try:
        last_action = BulkBetAction.objects.filter(
            user=request.user,
            is_undone=False
        ).first()
        
        if not last_action:
            return JsonResponse({
                'success': True,
                'has_action': False
            })
        
        return JsonResponse({
            'success': True,
            'has_action': True,
            'action': {
                'id': last_action.id,
                'type': last_action.action_type,
                'amount': str(last_action.amount),
                'total_bets': last_action.total_bets,
                'jodi_column': last_action.jodi_column,
                'jodi_type': last_action.jodi_type,
                'created_at': last_action.created_at.strftime('%Y-%m-%d %H:%M:%S')
            }
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_http_methods(["GET"])
def get_bet_summary(request):
    """Get summary statistics for user's bets"""
    try:
        user_bets = Bet.objects.filter(user=request.user)
        
        total_amount = sum(bet.amount for bet in user_bets)
        total_bets = user_bets.count()
        unique_numbers = user_bets.values('number').distinct().count()
        
        return JsonResponse({
            'success': True,
            'summary': {
                'total_amount': str(total_amount),
                'total_bets': total_bets,
                'unique_numbers': unique_numbers
            }
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def get_bet_total(request):
    try:
        total_amount = Bet.objects.filter(user=request.user).aggregate(Sum('amount'))['amount__sum'] or 0
        return JsonResponse({
            'success': True,
            'total_amount': total_amount
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })