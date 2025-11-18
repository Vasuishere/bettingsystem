# userbaseapp/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import CustomUser, Bet, BulkBetAction
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.cache import cache_page, cache_control
from django.db import transaction, connection
from django.db.models import Sum
from decimal import Decimal
import json
import os


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


Family_Pana_numbers = {
    'G1': [678, 123, 137, 268, 236, 178, 128, 367],
    'G2': [345, 890, 390, 458, 480, 359, 589, 340],
    'G3': [120, 567, 157, 260, 256, 170, 670, 125],
    'G4': [789, 234, 239, 478, 248, 379, 347, 289],
    'G5': [456, 190, 140, 569, 159, 460, 690, 145],
    'G6': [245, 290, 470, 579, 790, 457, 259, 240],
    'G7': [129, 147, 246, 679, 467, 269, 179, 124],
    'G8': [139, 148, 346, 689, 468, 369, 189, 134],
    'G9': [130, 158, 356, 680, 568, 360, 180, 135],
    'G10': [230, 258, 357, 780, 578, 370, 280, 235],
    'G11': [146, 119, 669, 169, 466, 114],
    'G12': [138, 336, 688, 368, 188, 133],
    'G13': [238, 337, 788, 378, 288, 233],
    'G14': [149, 446, 699, 469, 199, 144],
    'G15': [168, 113, 366, 136, 668, 118],
    'G16': [380, 335, 588, 358, 880, 330],
    'G17': [156, 110, 660, 160, 566, 115],
    'G18': [247, 229, 779, 279, 477, 224],
    'G19': [167, 112, 266, 126, 667, 117],
    'G20': [249, 447, 799, 479, 299, 244],
    'G21': [489, 344, 399, 349, 899, 448],
    'G22': [570, 255, 200, 250, 700, 557],
    'G23': [490, 445, 599, 459, 990, 440],
    'G24': [257, 220, 770, 270, 577, 225],
    'G25': [267, 122, 177, 127, 677, 226],
    'G26': [560, 100, 155, 150, 556, 600],
    'G27': [237, 228, 778, 278, 377, 223],
    'G28': [580, 300, 355, 350, 558, 800],
    'G29': [590, 400, 455, 450, 559, 900],
    'G30': [348, 339, 889, 389, 488, 334],
    'G31': [227, 777, 277, 222],
    'G32': [499, 444, 449, 999],
    'G33': [166, 111, 116, 666],
    'G34': [338, 888, 388, 333],
    'G35': [500, 555, 550, 000]
}


DADAR_NUMBERS = {
    1: [678],         
    2: [345],
    3: [120],
    4: [789],
    5: [456],
    6: [123],
    7: [890],
    8: [567],
    9: [234],
    10: [190]
}

# Eki/Beki number mappings
EKI_BEKI_NUMBERS = {
    'EKI': [137, 135, 139, 157, 159, 179, 357, 359, 379, 579],
    'BEKI': [246, 248, 240, 268, 260, 280, 468, 460, 480, 680]
}

# ABR Cut number mappings - 10 columns
ABR_CUT_NUMBERS = {
    1: [128, 146, 236, 245, 290, 380, 470, 489, 560],
    2: [129, 138, 147, 156, 237, 390, 570, 589, 679],
    3: [148, 238, 247, 256, 346, 490, 580, 670, 689],
    4: [130, 149, 158, 167, 239, 257, 347, 356, 590],
    5: [140, 168, 230, 249, 258, 267, 348, 690, 780],
    6: [150, 169, 178, 259, 349, 358, 367, 457, 790],
    7: [124, 160, 250, 269, 278, 340, 368, 458, 467],
    8: [125, 134, 170, 189, 279, 350, 369, 378, 459],
    9: [126, 180, 289, 270, 478, 568, 469, 450, 360],
    10: [127, 136, 145, 235, 370, 389, 479, 578, 569]
}

# Jodi Panel number mappings - 10 columns
JODI_PANEL_NUMBERS = {
    1: [128, 236, 290, 560, 489, 245, 678, 344, 100],
    2: [129, 589, 679, 237, 390, 150, 345, 778, 110],
    3: [238, 256, 376, 490, 670, 689, 120, 788, 445],
    4: [130, 167, 239, 247, 356, 590, 789, 455, 112],
    5: [140, 230, 267, 348, 690, 780, 456, 889, 122],
    6: [150, 178, 349, 367, 457, 790, 123, 556, 899],
    7: [124, 160, 278, 340, 458, 467, 890, 566, 223],
    8: [125, 170, 378, 134, 189, 459, 567, 233, 990],
    9: [126, 180, 289, 237, 450, 478, 568, 667, 900],
    10: [145, 235, 389, 569, 127, 578, 190, 677, 334]
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
    [127, 136, 145, 190, 235, 280, 370, 389, 460, 479, 569, 578, 118, 226, 244, 299, 334, 488, 550, 668, 677, '000']
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
    all_dadar = []
    for column in DADAR_NUMBERS.values():
        all_dadar.extend(column)
    return [str(num) for num in all_dadar]


def get_eki_beki_numbers(bet_type):
    """Get Eki or Beki numbers"""
    return [str(num) for num in EKI_BEKI_NUMBERS.get(bet_type, [])]


def get_abr_cut_numbers(column):
    """Get ABR Cut numbers for a specific column"""
    return [str(num) for num in ABR_CUT_NUMBERS.get(column, [])]


def get_jodi_panel_numbers(column, panel_type):
    """Get Jodi Panel numbers for a specific column
    panel_type: 6 (first 6 numbers), 7 (first 7 numbers), or 9 (all 9 numbers)
    """
    numbers = JODI_PANEL_NUMBERS.get(column, [])
    if panel_type == 6:
        return [str(num) for num in numbers[:6]]  # First 6 numbers
    elif panel_type == 7:
        return [str(num) for num in numbers[:7]]  # First 7 numbers
    else:  # panel_type == 9
        return [str(num) for num in numbers]  # All 9 numbers


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
@cache_control(max_age=3600, private=True)
def home(request):
    """Home page after successful login"""
    from datetime import datetime, timedelta
    
    # Prepare bazar choices for template
    bazar_choices = [
        {'value': 'SRIDEVI_OPEN', 'label': 'Sridevi Open'},
        {'value': 'SRIDEVI_CLOSED', 'label': 'Sridevi Closed'},
        {'value': 'TIME_OPEN', 'label': 'Time Open'},
        {'value': 'TIME_CLOSED', 'label': 'Time Closed'},
        {'value': 'DIVAS_MILAN_OPEN', 'label': 'Divas Milan Open'},
        {'value': 'DIVAS_MILAN_CLOSED', 'label': 'Divas Milan Closed'},
        {'value': 'KALYAN_OPEN', 'label': 'Kalyan Open'},
        {'value': 'KALYAN_CLOSED', 'label': 'Kalyan Closed'},
        {'value': 'NIGHT_MILAN_OPEN', 'label': 'Night Milan Open'},
        {'value': 'NIGHT_MILAN_CLOSED', 'label': 'Night Milan Closed'},
        {'value': 'MAIN_BAZAR', 'label': 'Main Bazar'},
        {'value': 'MAIN_BAZAR_CLOSED', 'label': 'Main Bazar Closed'},
    ]
    
    # Generate date options (last 30 days + next 7 days)
    today = datetime.now().date()
    date_options = []
    for i in range(30, -8, -1):  # 30 days ago to 7 days ahead
        date = today - timedelta(days=i)
        date_options.append({
            'value': date.strftime('%Y-%m-%d'),
            'label': date.strftime('%d %b %Y'),
            'is_today': date == today
        })
    
    # Row labels for spreadsheet
    row_labels = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V']
    
    # Bazar names mapping
    bazar_names = {
        'SRIDEVI_OPEN': 'Sridevi Open',
        'SRIDEVI_CLOSED': 'Sridevi Closed',
        'TIME_OPEN': 'Time Open',
        'TIME_CLOSED': 'Time Closed',
        'DIVAS_MILAN_OPEN': 'Divas Milan Open',
        'DIVAS_MILAN_CLOSED': 'Divas Milan Closed',
        'KALYAN_OPEN': 'Kalyan Open',
        'KALYAN_CLOSED': 'Kalyan Closed',
        'NIGHT_MILAN_OPEN': 'Night Milan Open',
        'NIGHT_MILAN_CLOSED': 'Night Milan Closed',
        'MAIN_BAZAR': 'Main Bazar',
        'MAIN_BAZAR_CLOSED': 'Main Bazar Closed'
    }
    
    return render(request, 'userbaseapp/home.html', {
        'ALL_COLUMN_DATA': json.dumps(ALL_COLUMN_DATA),
        'bazar_choices': bazar_choices,
        'date_options': date_options,
        'row_labels': row_labels,
        'bazar_names_json': json.dumps(bazar_names),
        'current_date': today.strftime('%Y-%m-%d')
    })


def logout_view(request):
    auth_logout(request)
    return redirect('/')


@login_required
@require_http_methods(["POST"])
def place_bet(request):
    """Save a single bet to the database"""
    try:
        data = json.loads(request.body.decode('utf-8'))
        number = data.get('number')
        amount = data.get('amount')
        bazar = data.get('bazar', 'SRIDEVI_OPEN')
        date_str = data.get('date')

        if not number or not amount:
            return JsonResponse({'error': 'Missing number or amount'}, status=400)

        amount = Decimal(str(amount))
        if amount <= 0:
            return JsonResponse({'error': 'Amount must be greater than 0'}, status=400)

        # Parse date if provided
        from django.utils import timezone
        bet_date = timezone.now().date()
        if date_str:
            from datetime import datetime
            bet_date = datetime.fromisoformat(date_str).date()

        bet = Bet.objects.create(
            user=request.user,
            number=str(number),
            amount=amount,
            bet_type='SINGLE',
            bazar=bazar,
            bet_date=bet_date
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
    """Place bulk bets (SP, DP, Jodi Vagar, Dadar, Eki, Beki, or ABR Cut)"""
    try:
        data = json.loads(request.body.decode('utf-8'))
        bet_type = data.get('type')  # 'SP', 'DP', 'JODI', 'DADAR', 'EKI', 'BEKI', or 'ABR_CUT'
        amount = data.get('amount')
        bazar = data.get('bazar', 'SRIDEVI_OPEN')
        date_str = data.get('date')

        if not bet_type or not amount:
            return JsonResponse({'error': 'Missing type or amount'}, status=400)

        amount = Decimal(str(amount))
        if amount <= 0:
            return JsonResponse({'error': 'Amount must be greater than 0'}, status=400)

        # Parse date if provided
        from django.utils import timezone
        bet_date = timezone.now().date()
        if date_str:
            from datetime import datetime
            bet_date = datetime.fromisoformat(date_str).date()

        # Determine which numbers to bet on
        if bet_type == 'SP':
            columns = data.get('columns')  # Support multiple columns
            if columns and isinstance(columns, list):
                # Multi-column SP
                numbers = []
                for column in columns:
                    column_index = int(column) - 1
                    if 0 <= column_index < 10:
                        column_data = ALL_COLUMN_DATA[column_index]
                        # Get SP numbers from this column (first 12 numbers)
                        sp_from_column = [str(n) for n in column_data[0:12]]
                        numbers.extend(sp_from_column)
                # Remove duplicates
                seen = set()
                numbers = [x for x in numbers if not (x in seen or seen.add(x))]
            else:
                numbers = get_sp_numbers()
        elif bet_type == 'DP':
            columns = data.get('columns')  # Support multiple columns
            if columns and isinstance(columns, list):
                # Multi-column DP
                numbers = []
                for column in columns:
                    column_index = int(column) - 1
                    if 0 <= column_index < 10:
                        column_data = ALL_COLUMN_DATA[column_index]
                        # Get DP numbers from this column (last 10 numbers, positions 12-21)
                        dp_from_column = [str(n) for n in column_data[12:22]]
                        numbers.extend(dp_from_column)
                # Remove duplicates
                seen = set()
                numbers = [x for x in numbers if not (x in seen or seen.add(x))]
            else:
                numbers = get_dp_numbers()
        elif bet_type == 'JODI':
            columns = data.get('columns')  # Support multiple columns
            jodi_type = data.get('jodi_type')  # 5, 7, or 12
            
            if not columns or not jodi_type:
                return JsonResponse({'error': 'Missing columns or jodi_type'}, status=400)
            
            # Ensure columns is a list
            if not isinstance(columns, list):
                columns = [columns]
            
            jodi_type = int(jodi_type)
            
            # Collect all numbers from all selected columns
            numbers = []
            for column in columns:
                column = int(column)
                if column not in JODI_VAGAR_NUMBERS:
                    return JsonResponse({'error': f'Invalid column {column}'}, status=400)
                
                all_jodi_numbers = JODI_VAGAR_NUMBERS[column]
                
                if jodi_type == 5:
                    numbers.extend([str(n) for n in all_jodi_numbers[:5]])
                elif jodi_type == 7:
                    numbers.extend([str(n) for n in all_jodi_numbers[-7:]])
                elif jodi_type == 12:
                    numbers.extend([str(n) for n in all_jodi_numbers])
                else:
                    return JsonResponse({'error': 'Invalid jodi_type'}, status=400)
            
            # Remove duplicates while preserving order
            seen = set()
            numbers = [x for x in numbers if not (x in seen or seen.add(x))]
        elif bet_type == 'DADAR':
            # Always bet on all 10 Dadar numbers
            numbers = get_dadar_numbers()
        elif bet_type in ['EKI', 'BEKI']:
            numbers = get_eki_beki_numbers(bet_type)
        elif bet_type == 'ABR_CUT':
            columns = data.get('columns')  # Support multiple columns
            
            if not columns:
                return JsonResponse({'error': 'Missing columns for ABR Cut'}, status=400)
            
            # Ensure columns is a list
            if not isinstance(columns, list):
                columns = [columns]
            
            # Collect all numbers from all selected columns
            numbers = []
            for column in columns:
                column = int(column)
                if column not in ABR_CUT_NUMBERS:
                    return JsonResponse({'error': f'Invalid column {column} for ABR Cut'}, status=400)
                numbers.extend(get_abr_cut_numbers(column))
            
            # Remove duplicates while preserving order
            seen = set()
            numbers = [x for x in numbers if not (x in seen or seen.add(x))]
        elif bet_type == 'JODI_PANEL':
            columns = data.get('columns')  # Support multiple columns
            panel_type = data.get('panel_type')  # 6, 7, or 9
            
            if not columns or not panel_type:
                return JsonResponse({'error': 'Missing columns or panel_type for Jodi Panel'}, status=400)
            
            # Ensure columns is a list
            if not isinstance(columns, list):
                columns = [columns]
            
            panel_type = int(panel_type)
            if panel_type not in [6, 7, 9]:
                return JsonResponse({'error': 'Invalid panel_type. Must be 6, 7, or 9'}, status=400)
            
            # Collect all numbers from all selected columns
            numbers = []
            for column in columns:
                column = int(column)
                if column not in JODI_PANEL_NUMBERS:
                    return JsonResponse({'error': f'Invalid column {column} for Jodi Panel'}, status=400)
                numbers.extend(get_jodi_panel_numbers(column, panel_type))
            
            # Remove duplicates while preserving order
            seen = set()
            numbers = [x for x in numbers if not (x in seen or seen.add(x))]
        else:
            return JsonResponse({'error': 'Invalid bet type'}, status=400)

        # Create bulk action record
        # Store first column for tracking purposes
        jodi_column = None
        if bet_type in ['JODI', 'DADAR', 'ABR_CUT', 'JODI_PANEL']:
            columns = data.get('columns')
            if columns and isinstance(columns, list) and len(columns) > 0:
                jodi_column = columns[0]
        
        bulk_action = BulkBetAction.objects.create(
            user=request.user,
            action_type=bet_type,
            amount=amount,
            total_bets=len(numbers),
            jodi_column=jodi_column,
            jodi_type=data.get('jodi_type') if bet_type == 'JODI' else (data.get('panel_type') if bet_type == 'JODI_PANEL' else None),
            bazar=bazar,
            action_date=bet_date
        )

        # Create all bets
        bets_created = []
        
        # Determine sub_type for tracking
        sub_type = None
        if bet_type == 'JODI':
            sub_type = str(data.get('jodi_type'))  # '5', '7', or '12'
        elif bet_type == 'JODI_PANEL':
            sub_type = str(data.get('panel_type'))  # '6' or '7'
        elif bet_type in ['EKI', 'BEKI', 'DADAR']:
            sub_type = bet_type  # Store EKI, BEKI, or DADAR as sub_type
        
        # Get all columns for multi-column bets
        all_columns = data.get('columns', [])
        if not isinstance(all_columns, list):
            all_columns = [all_columns] if all_columns else []
        
        for number in numbers:
            # Determine which column this number belongs to (for column-based bet types)
            column_num = None
            
            # For SP and DP, detect column from ALL_COLUMN_DATA if columns were selected
            if bet_type in ['SP', 'DP'] and all_columns:
                for col in all_columns:
                    col_int = int(col)
                    if 1 <= col_int <= 10:
                        column_data = ALL_COLUMN_DATA[col_int - 1]
                        if bet_type == 'SP':
                            # Check if number is in first 12 positions (SP numbers)
                            if number in [str(n) for n in column_data[0:12]]:
                                column_num = col_int
                                break
                        elif bet_type == 'DP':
                            # Check if number is in positions 12-21 (DP numbers)
                            if number in [str(n) for n in column_data[12:22]]:
                                column_num = col_int
                                break
            
            # For other column-based bet types (only if columns were provided)
            elif bet_type in ['JODI', 'ABR_CUT', 'JODI_PANEL'] and all_columns:
                # Find which column contains this number
                for col in all_columns:
                    col_int = int(col)
                    if bet_type == 'JODI' and col_int in JODI_VAGAR_NUMBERS:
                        if int(number) in JODI_VAGAR_NUMBERS[col_int]:
                            column_num = col_int
                            break
                    elif bet_type == 'ABR_CUT' and col_int in ABR_CUT_NUMBERS:
                        if int(number) in ABR_CUT_NUMBERS[col_int]:
                            column_num = col_int
                            break
                    elif bet_type == 'JODI_PANEL' and col_int in JODI_PANEL_NUMBERS:
                        if int(number) in JODI_PANEL_NUMBERS[col_int]:
                            column_num = col_int
                            break
            
            bet = Bet.objects.create(
                user=request.user,
                number=str(number),
                amount=amount,
                bulk_action=bulk_action,
                bet_type=bet_type,
                column_number=column_num,
                sub_type=sub_type,
                bazar=bazar,
                bet_date=bet_date
            )
            # Convert to IST for display
            from django.utils import timezone as tz
            local_time = tz.localtime(bet.created_at)
            bets_created.append({
                'id': bet.id,
                'number': bet.number,
                'amount': str(bet.amount),
                'bet_type': bet.bet_type,
                'column': column_num,
                'created_at': local_time.strftime('%Y-%m-%d %I:%M:%S %p IST')
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
        bazar = request.GET.get('bazar', 'SRIDEVI_OPEN')
        date_str = request.GET.get('date')
        
        # Parse date if provided
        from django.utils import timezone
        bet_date = timezone.now().date()
        if date_str:
            from datetime import datetime
            bet_date = datetime.fromisoformat(date_str).date()
        
        # Optimized query - only fetch needed fields and use index
        user_bets = Bet.objects.filter(
            user=request.user,
            bazar=bazar,
            bet_date=bet_date
        ).only(
            'id', 'number', 'amount', 'created_at', 
            'bet_type', 'column_number', 'sub_type'
        ).order_by('-created_at')
        
        bets_dict = {}
        for bet in user_bets:
            if bet.number not in bets_dict:
                bets_dict[bet.number] = {
                    'total': 0,
                    'history': []
                }
            bets_dict[bet.number]['total'] += float(bet.amount)
            # Convert to IST for display
            local_time = timezone.localtime(bet.created_at)
            bets_dict[bet.number]['history'].append({
                'id': bet.id,
                'amount': float(bet.amount),
                'created_at': local_time.strftime('%Y-%m-%d %I:%M:%S %p IST'),
                'bet_type': bet.bet_type,
                'column': bet.column_number,
                'sub_type': bet.sub_type
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
@transaction.atomic
def undo_bulk_action(request):
    """Undo/Delete a bulk betting action"""
    try:
        data = json.loads(request.body.decode('utf-8'))
        bulk_action_id = data.get('bulk_action_id')

        if not bulk_action_id:
            return JsonResponse({'success': False, 'message': 'Missing bulk_action_id'}, status=400)

        # Find the bulk action
        bulk_action = BulkBetAction.objects.filter(
            id=bulk_action_id, 
            user=request.user
        ).first()
        
        if not bulk_action:
            return JsonResponse({'success': False, 'message': 'Bulk action not found or does not belong to you'}, status=404)
        
        # Check if already undone
        if bulk_action.is_undone:
            return JsonResponse({'success': False, 'message': 'This bulk action has already been deleted'}, status=400)
        
        # Get count before deletion for message
        bet_count = bulk_action.bets.count()
        
        # Delete all associated bets and mark as undone
        success, message = bulk_action.undo()

        if success:
            return JsonResponse({
                'success': True,
                'message': f'Successfully deleted bulk action with {bet_count} bets'
            })
        else:
            return JsonResponse({
                'success': False,
                'message': message
            }, status=400)

    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': 'Invalid JSON data'}, status=400)
    except Exception as e:
        # Log the error for debugging
        print(f"Error in undo_bulk_action: {str(e)}")
        return JsonResponse({'success': False, 'message': f'Server error: {str(e)}'}, status=500)


@login_required
@require_http_methods(["GET"])
def get_last_bulk_action(request):
    """Get the last bulk action for undo button visibility"""
    try:
        bazar = request.GET.get('bazar', 'SRIDEVI_OPEN')
        date_str = request.GET.get('date')
        
        # Parse date if provided
        from django.utils import timezone
        action_date = timezone.now().date()
        if date_str:
            from datetime import datetime
            action_date = datetime.fromisoformat(date_str).date()
        
        # Optimized query - only fetch needed fields
        last_action = BulkBetAction.objects.filter(
            user=request.user,
            is_undone=False,
            bazar=bazar,
            action_date=action_date
        ).only(
            'id', 'action_type', 'amount', 'total_bets',
            'jodi_column', 'jodi_type', 'created_at'
        ).first()
        
        if not last_action:
            return JsonResponse({
                'success': True,
                'has_action': False
            })
        
        # Convert to IST for display
        from django.utils import timezone as tz
        local_time = tz.localtime(last_action.created_at)
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
                'created_at': local_time.strftime('%Y-%m-%d %I:%M:%S %p IST')
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
        bazar = request.GET.get('bazar', 'SRIDEVI_OPEN')
        date_str = request.GET.get('date')
        
        # Parse date if provided
        from django.utils import timezone
        bet_date = timezone.now().date()
        if date_str:
            from datetime import datetime
            bet_date = datetime.fromisoformat(date_str).date()
        
        # Optimized aggregation - uses database-level SUM for better performance
        total_amount = Bet.objects.filter(
            user=request.user,
            bazar=bazar,
            bet_date=bet_date
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        return JsonResponse({
            'success': True,
            'total_amount': float(total_amount)
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


@login_required
@require_http_methods(["GET"])
def get_all_bet_totals(request):
    """Get bet totals for all numbers grouped by number - for real-time sync across devices"""
    try:
        bazar = request.GET.get('bazar', 'SRIDEVI_OPEN')
        date_str = request.GET.get('date')
        
        # Parse date if provided
        from django.utils import timezone
        bet_date = timezone.now().date()
        if date_str:
            from datetime import datetime
            bet_date = datetime.fromisoformat(date_str).date()
        
        # Optimized query - group by number and sum amounts at database level
        from django.db.models import Sum
        bet_totals = Bet.objects.filter(
            user=request.user,
            bazar=bazar,
            bet_date=bet_date
        ).values('number').annotate(
            total=Sum('amount')
        ).order_by('number')
        
        # Convert to dictionary for easy lookup: {number: total}
        totals_dict = {}
        for item in bet_totals:
            totals_dict[item['number']] = float(item['total'])
        
        return JsonResponse({
            'success': True,
            'bet_totals': totals_dict
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@require_http_methods(["GET"])
def get_bulk_action_history(request):
    """Get all bulk action history for the current user with optional bazar and date filtering"""
    try:
        # Get filter parameters
        bazar = request.GET.get('bazar', None)
        date_str = request.GET.get('date', None)
        
        # Start with base query
        bulk_actions = BulkBetAction.objects.filter(user=request.user).select_related('user')
        
        # Apply bazar filter if provided
        if bazar:
            bulk_actions = bulk_actions.filter(bazar=bazar)
        
        # Apply date filter if provided
        if date_str:
            from datetime import datetime
            try:
                filter_date = datetime.fromisoformat(date_str).date()
                bulk_actions = bulk_actions.filter(action_date=filter_date)
            except ValueError:
                pass  # Invalid date format, skip filtering
        
        # Order by newest first
        bulk_actions = bulk_actions.order_by('-created_at')
        
        history_data = []
        for action in bulk_actions:
            # Convert to IST for display
            from django.utils import timezone as tz
            local_time = tz.localtime(action.created_at)
            history_data.append({
                'id': action.id,
                'action_type': action.action_type,
                'amount': str(action.amount),
                'total_bets': action.total_bets,
                'jodi_column': action.jodi_column,
                'jodi_type': action.jodi_type,
                'created_at': local_time.strftime('%Y-%m-%d %I:%M:%S %p IST'),
                'is_undone': action.is_undone,
                'bazar': action.bazar,
                'action_date': action.action_date.strftime('%Y-%m-%d') if action.action_date else None
            })
        
        return JsonResponse({
            'success': True,
            'history': history_data,
            'count': len(history_data)
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })
    

def generate_three_digit_numbers(digits_string):
    """
    Generate 3-digit numbers from given digits with custom rules:
    - Custom order: 1 < 2 < 3 < 4 < 5 < 6 < 7 < 8 < 9 < 0
    - Pattern: a < b < c (strictly increasing)
    - 0 can only appear at position c (last position)
    - Digits can repeat
    """
    
    # Define custom order: 1 is smallest, 0 is largest
    order_map = {'1': 1, '2': 2, '3': 3, '4': 4, '5': 5, 
                 '6': 6, '7': 7, '8': 8, '9': 9, '0': 10}
    
    # Get unique digits from input
    available_digits = list(set(digits_string))
    
    valid_numbers = []
    
    # Generate all possible 3-digit combinations
    for a in available_digits:
        for b in available_digits:
            for c in available_digits:
                # Rule: 0 can only be at position c
                if a == '0' or b == '0':
                    continue
                
                # Rule: a < b < c (using custom order)
                if order_map[a] < order_map[b] < order_map[c]:
                    number = a + b + c
                    valid_numbers.append(number)
    
    return sorted(valid_numbers)


def find_sp_numbers_with_digit(digit):
    """
    Find all SP numbers (first 12 from each column) that contain the given digit.
    Common Pana 36 - searches only in SP numbers.
    
    Args:
        digit: Single digit (0-9) as string or int
        
    Returns:
        List of SP numbers containing the digit, sorted
    """
    digit_str = str(digit)
    
    # Validate input
    if not digit_str.isdigit() or len(digit_str) != 1:
        return []
    
    sp_numbers_with_digit = []
    
    # Iterate through all columns in ALL_COLUMN_DATA
    for column in ALL_COLUMN_DATA:
        # Get first 12 numbers (SP numbers) from each column
        sp_numbers = column[0:12]
        
        # Check if the digit appears in any of these SP numbers
        for num in sp_numbers:
            num_str = str(num)
            if digit_str in num_str:
                sp_numbers_with_digit.append(num_str)
    
    # Return sorted unique numbers
    return sorted(list(set(sp_numbers_with_digit)))


def find_sp_dp_numbers_with_digit(digit):
    """
    Find all SP + DP numbers (first 22 rows from each column) that contain the given digit.
    Common Pana 56 - searches in both SP and DP numbers.
    
    Args:
        digit: Single digit (0-9) as string or int
        
    Returns:
        List of SP + DP numbers containing the digit, sorted
    """
    digit_str = str(digit)
    
    # Validate input
    if not digit_str.isdigit() or len(digit_str) != 1:
        return []
    
    sp_dp_numbers_with_digit = []
    
    # Iterate through all columns in ALL_COLUMN_DATA
    for column in ALL_COLUMN_DATA:
        # Get first 22 numbers (SP + DP numbers) from each column
        sp_dp_numbers = column[0:22]
        
        # Check if the digit appears in any of these numbers
        for num in sp_dp_numbers:
            num_str = str(num)
            if digit_str in num_str:
                sp_dp_numbers_with_digit.append(num_str)
    
    # Return sorted unique numbers
    return sorted(list(set(sp_dp_numbers_with_digit)))


def find_family_group_by_number(number):
    """
    Find the family group (G1-G35) that contains the given number.
    
    Args:
        number: 3-digit number as string or int
        
    Returns:
        tuple: (family_name, family_numbers) or (None, None) if not found
    """
    number_int = int(number)
    
    for family_name, family_numbers in Family_Pana_numbers.items():
        if number_int in family_numbers:
            return family_name, family_numbers
    
    return None, None


@login_required
@require_http_methods(["POST"])
def generate_motar_numbers(request):
    """API endpoint to generate Motar numbers from input digits"""
    try:
        data = json.loads(request.body.decode('utf-8'))
        digits = data.get('digits', '')
        
        # Validate input
        if not digits or not digits.isdigit():
            return JsonResponse({'error': 'Invalid digits input'}, status=400)
        
        if len(digits) < 4 or len(digits) > 10:
            return JsonResponse({'error': 'Digits must be 4-10 characters long'}, status=400)
        
        # Generate numbers
        numbers = generate_three_digit_numbers(digits)
        
        return JsonResponse({
            'success': True,
            'numbers': numbers,
            'count': len(numbers)
        })
    
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_http_methods(["POST"])
def find_comman_pana_numbers(request):
    """API endpoint to find numbers containing a specific digit
    Supports both Common Pana 36 (SP only) and Common Pana 56 (SP + DP)
    """
    try:
        data = json.loads(request.body.decode('utf-8'))
        digit = data.get('digit')
        bet_type = data.get('type', '36')  # '36' or '56', default to 36
        
        # Validate input
        if digit is None:
            return JsonResponse({'error': 'Missing digit parameter'}, status=400)
        
        digit_str = str(digit)
        if not digit_str.isdigit() or len(digit_str) != 1:
            return JsonResponse({'error': 'Digit must be a single digit (0-9)'}, status=400)
        
        # Find numbers based on type
        if bet_type == '56':
            numbers = find_sp_dp_numbers_with_digit(digit)
            bet_name = 'Common Pana 56'
        else:
            numbers = find_sp_numbers_with_digit(digit)
            bet_name = 'Common Pana 36'
        
        return JsonResponse({
            'success': True,
            'numbers': numbers,
            'count': len(numbers),
            'digit': digit_str,
            'type': bet_type,
            'bet_name': bet_name
        })
    
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_http_methods(["POST"])
@transaction.atomic
def place_motar_bet(request):
    """Place bulk Motar bet - generate numbers and place all bets in one transaction"""
    try:
        data = json.loads(request.body.decode('utf-8'))
        digits = data.get('digits', '')
        amount = data.get('amount')
        bazar = data.get('bazar', 'SRIDEVI_OPEN')
        date_str = data.get('date')
        
        # Validate input
        if not digits or not digits.isdigit():
            return JsonResponse({'error': 'Invalid digits input'}, status=400)
        
        if len(digits) < 4 or len(digits) > 10:
            return JsonResponse({'error': 'Digits must be 4-10 characters long'}, status=400)
        
        if not amount:
            return JsonResponse({'error': 'Missing amount'}, status=400)
        
        amount = Decimal(str(amount))
        if amount <= 0:
            return JsonResponse({'error': 'Amount must be greater than 0'}, status=400)
        
        # Parse date if provided
        from django.utils import timezone
        bet_date = timezone.now().date()
        if date_str:
            from datetime import datetime
            bet_date = datetime.fromisoformat(date_str).date()
        
        # Generate numbers server-side
        numbers = generate_three_digit_numbers(digits)
        
        if not numbers:
            return JsonResponse({'error': 'No valid numbers generated'}, status=400)
        
        # Create bulk action record for Motar
        bulk_action = BulkBetAction.objects.create(
            user=request.user,
            action_type='MOTAR',
            amount=amount,
            total_bets=len(numbers),
            bazar=bazar,
            action_date=bet_date
        )
        
        # Create bets and track IDs for undo functionality
        bet_ids = []
        bets_created = []
        
        for number in numbers:
            bet = Bet.objects.create(
                user=request.user,
                number=str(number),
                amount=amount,
                bet_type='MOTAR',
                bulk_action=bulk_action,
                bazar=bazar,
                bet_date=bet_date
            )
            bet_ids.append(bet.id)
            bets_created.append({
                'bet_id': bet.id,
                'number': bet.number,
                'amount': str(bet.amount)
            })
        
        return JsonResponse({
            'success': True,
            'message': f'{len(numbers)} Motar bets placed successfully',
            'total_bets': len(numbers),
            'bet_ids': bet_ids,
            'bets': bets_created,
            'digits': digits,
            'bulk_action_id': bulk_action.id
        })
    
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_http_methods(["POST"])
@transaction.atomic
def place_comman_pana_bet(request):
    """Place bulk Common Pana bet - supports both 36 (SP only) and 56 (SP + DP)"""
    try:
        data = json.loads(request.body.decode('utf-8'))
        digit = data.get('digit')
        amount = data.get('amount')
        bet_type = data.get('type', '36')  # '36' or '56', default to 36
        bazar = data.get('bazar', 'SRIDEVI_OPEN')
        date_str = data.get('date')
        
        # Validate input
        if digit is None:
            return JsonResponse({'error': 'Missing digit parameter'}, status=400)
        
        digit_str = str(digit)
        if not digit_str.isdigit() or len(digit_str) != 1:
            return JsonResponse({'error': 'Digit must be a single digit (0-9)'}, status=400)
        
        if not amount:
            return JsonResponse({'error': 'Missing amount'}, status=400)
        
        amount = Decimal(str(amount))
        if amount <= 0:
            return JsonResponse({'error': 'Amount must be greater than 0'}, status=400)
        
        # Parse date if provided
        from django.utils import timezone
        bet_date = timezone.now().date()
        if date_str:
            from datetime import datetime
            bet_date = datetime.fromisoformat(date_str).date()
        
        # Find numbers based on type
        if bet_type == '56':
            numbers = find_sp_dp_numbers_with_digit(digit)
            action_type = 'COMMAN_PANA_56'
            bet_type_name = 'COMMAN_PANA_56'
            message_type = 'Common Pana 56'
        else:
            numbers = find_sp_numbers_with_digit(digit)
            action_type = 'COMMAN_PANA_36'
            bet_type_name = 'COMMAN_PANA_36'
            message_type = 'Common Pana 36'
        
        if not numbers:
            return JsonResponse({'error': f'No numbers contain digit {digit}'}, status=400)
        
        # Create bulk action record
        bulk_action = BulkBetAction.objects.create(
            user=request.user,
            action_type=action_type,
            amount=amount,
            total_bets=len(numbers),
            jodi_type=int(digit),  # Store the digit in jodi_type field for reference
            bazar=bazar,
            action_date=bet_date
        )
        
        # Create bets and track IDs for undo functionality
        bet_ids = []
        bets_created = []
        
        for number in numbers:
            bet = Bet.objects.create(
                user=request.user,
                number=str(number),
                amount=amount,
                bet_type=bet_type_name,
                bulk_action=bulk_action,
                bazar=bazar,
                bet_date=bet_date
            )
            bet_ids.append(bet.id)
            bets_created.append({
                'bet_id': bet.id,
                'number': bet.number,
                'amount': str(bet.amount)
            })
        
        return JsonResponse({
            'success': True,
            'message': f'{len(numbers)} {message_type} bets placed for digit {digit}',
            'total_bets': len(numbers),
            'bet_ids': bet_ids,
            'bets': bets_created,
            'digit': digit_str,
            'type': bet_type,
            'bulk_action_id': bulk_action.id
        })
    
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_http_methods(["POST"])
@transaction.atomic
def place_set_pana_bet(request):
    """Place Set Pana bet - bets on all numbers in a family group"""
    try:
        data = json.loads(request.body.decode('utf-8'))
        number = data.get('number')
        amount = data.get('amount')
        bazar = data.get('bazar', 'SRIDEVI_OPEN')
        date_str = data.get('date')
        
        # Validate inputs
        if not number:
            return JsonResponse({'error': 'Missing number'}, status=400)
        
        # Validate 3-digit number
        number_str = str(number).strip()
        if not number_str.isdigit() or len(number_str) != 3:
            return JsonResponse({'error': 'Number must be exactly 3 digits'}, status=400)
        
        if not amount:
            return JsonResponse({'error': 'Missing amount'}, status=400)
        
        amount = Decimal(str(amount))
        if amount <= 0:
            return JsonResponse({'error': 'Amount must be greater than 0'}, status=400)
        
        # Parse date if provided
        from django.utils import timezone
        bet_date = timezone.now().date()
        if date_str:
            from datetime import datetime
            bet_date = datetime.fromisoformat(date_str).date()
        
        # Find the family group
        family_name, family_numbers = find_family_group_by_number(number)
        
        if not family_name:
            return JsonResponse({
                'error': f'Number {number} not found in any family group'
            }, status=400)
        
        # Create bulk action record
        bulk_action = BulkBetAction.objects.create(
            user=request.user,
            action_type='SET_PANA',
            amount=amount,
            total_bets=len(family_numbers),
            bazar=bazar,
            action_date=bet_date
        )
        
        # Create bets for all numbers in the family
        bet_ids = []
        bets_created = []
        
        for num in family_numbers:
            bet = Bet.objects.create(
                user=request.user,
                number=str(num),
                amount=amount,
                bet_type='SET_PANA',
                bulk_action=bulk_action,
                bazar=bazar,
                bet_date=bet_date
            )
            bet_ids.append(bet.id)
            bets_created.append({
                'bet_id': bet.id,
                'number': bet.number,
                'amount': str(bet.amount)
            })
        
        return JsonResponse({
            'success': True,
            'message': f'{len(family_numbers)} Set Pana bets placed for family {family_name}',
            'total_bets': len(family_numbers),
            'bet_ids': bet_ids,
            'bets': bets_created,
            'family_name': family_name,
            'family_numbers': [str(n) for n in family_numbers],
            'bulk_action_id': bulk_action.id
        })
    
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_http_methods(["GET"])
def get_database_storage(request):
    """Get database storage usage information"""
    try:
        # Check if using PostgreSQL (production/Aiven) or SQLite (development)
        db_engine = connection.settings_dict['ENGINE']
        
        if 'postgresql' in db_engine:
            # For PostgreSQL (Aiven)
            with connection.cursor() as cursor:
                # Get database size in bytes
                cursor.execute("SELECT pg_database_size(current_database());")
                size_bytes = cursor.fetchone()[0]
                
            # Convert to MB
            size_mb = size_bytes / (1024 * 1024)
            # Aiven free tier limit: 1 GB = 1024 MB
            max_storage_mb = 1024
            percentage = (size_mb / max_storage_mb) * 100
            
            return JsonResponse({
                'success': True,
                'storage_used_mb': round(size_mb, 2),
                'storage_total_mb': max_storage_mb,
                'percentage': round(percentage, 2),
                'database_type': 'PostgreSQL (Aiven)'
            })
        else:
            # For SQLite (development)
            db_path = connection.settings_dict['NAME']
            if os.path.exists(db_path):
                size_bytes = os.path.getsize(db_path)
                size_mb = size_bytes / (1024 * 1024)
                # Use same 1GB limit for consistency
                max_storage_mb = 1024
                percentage = (size_mb / max_storage_mb) * 100
                
                return JsonResponse({
                    'success': True,
                    'storage_used_mb': round(size_mb, 2),
                    'storage_total_mb': max_storage_mb,
                    'percentage': round(percentage, 2),
                    'database_type': 'SQLite (Development)'
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': 'Database file not found'
                }, status=404)
                
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
