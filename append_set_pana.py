"""Temporary script to append Set Pana function to views.py"""

set_pana_code = '''

@login_required
@require_http_methods(["POST"])
@transaction.atomic
def place_set_pana_bet(request):
    """Place Set Pana bet - bets on all numbers in a family group"""
    try:
        data = json.loads(request.body.decode('utf-8'))
        number = data.get('number')
        amount = data.get('amount')
        
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
            total_bets=len(family_numbers)
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
                bulk_action=bulk_action
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
'''

# Append to views.py
with open(r'c:\Users\risha\Documents\vasu\bett\userbaseapp\views.py', 'a', encoding='utf-8') as f:
    f.write(set_pana_code)

print("Set Pana function added successfully!")
