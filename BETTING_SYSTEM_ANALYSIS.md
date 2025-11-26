# Betting System Deep Analysis - Django to Node.js Migration Guide

## Executive Summary
This document provides a comprehensive analysis of the Django betting application, detailing how bets are placed, number selection mechanisms, bet types, and the complete backend architecture. This analysis is critical for migrating to a Node.js/Next.js implementation.

---

## Table of Contents
1. [System Architecture Overview](#system-architecture-overview)
2. [Data Models](#data-models)
3. [Bet Types & Number Selection](#bet-types--number-selection)
4. [API Endpoints](#api-endpoints)
5. [Number Selection Logic](#number-selection-logic)
6. [UI/UX Flow](#uiux-flow)
7. [Migration Checklist](#migration-checklist)

---

## System Architecture Overview

### Core Components
1. **Backend**: Django (Python) with Django ORM
2. **Frontend**: Server-rendered HTML with JavaScript (Tailwind CSS)
3. **Database**: SQLite (dev) / PostgreSQL (production - Aiven)
4. **State Management**: Client-side JavaScript with localStorage

### Data Flow
```
User Interface (home.html)
    ↓
JavaScript Event Handlers
    ↓
AJAX/Fetch API Calls (CSRF Protected)
    ↓
Django Views (views.py)
    ↓
Django Models (models.py)
    ↓
Database (SQLite/PostgreSQL)
```

---

## Data Models

### 1. CustomUser Model
```python
class CustomUser(AbstractUser):
    """Extended Django User with email/username authentication"""
    # Inherits: username, email, password, first_name, last_name
```

### 2. Bet Model (Primary Entity)
**Purpose**: Stores individual bet transactions

**Key Fields**:
- `user`: ForeignKey to CustomUser (with index)
- `number`: CharField (3-digit betting number, e.g., "137", "000")
- `amount`: DecimalField (bet amount)
- `bazar`: CharField - 12 bazars available:
  - SRIDEVI_OPEN, SRIDEVI_CLOSED
  - TIME_OPEN, TIME_CLOSED
  - DIVAS_MILAN_OPEN, DIVAS_MILAN_CLOSED
  - KALYAN_OPEN, KALYAN_CLOSED
  - NIGHT_MILAN_OPEN, NIGHT_MILAN_CLOSED
  - MAIN_BAZAR, MAIN_BAZAR_CLOSED
- `bet_date`: DateField (when bet was placed)
- `bet_type`: CharField - Types:
  - SINGLE: Direct number bet
  - SP: All SP numbers (first 12 rows)
  - DP: All DP numbers (rows 13-22)
  - JODI: Jodi Vagar (column-based)
  - DADAR: Dadar numbers (10 specific numbers)
  - EKI: Eki numbers (odd-based pattern)
  - BEKI: Beki numbers (even-based pattern)
  - ABR_CUT: ABR Cut (9 numbers per column)
  - JODI_PANEL: Jodi Panel (6/7/9 numbers)
  - MOTAR: Generated from 4-10 digit input
  - COMMAN_PANA_36: Common Pana (SP only)
  - COMMAN_PANA_56: Common Pana (SP + DP)
  - SET_PANA: Family group betting
  - COLUMN: Column number betting
- `column_number`: Integer (1-10, tracks which column)
- `sub_type`: CharField (stores jodi_type: 5/7/12 or panel_type: 6/7)
- `bulk_action`: ForeignKey to BulkBetAction (for undo functionality)
- `status`: CharField (ACTIVE, WON, LOST, CANCELLED, PENDING)
- `is_deleted`: Boolean (soft delete flag)

**Critical Indexes**:
```python
indexes = [
    ('user', 'number'),
    ('user', '-created_at'),
    ('user', 'bazar', 'bet_date'),  # Most important for queries
    ('bet_type', 'column_number'),
]
```

### 3. BulkBetAction Model
**Purpose**: Tracks bulk bet operations for undo functionality

**Key Fields**:
- `user`: ForeignKey to CustomUser
- `action_type`: Same as Bet.bet_type choices
- `amount`: Decimal (amount per bet)
- `total_bets`: Integer (count of bets created)
- `bazar`: CharField (same as Bet)
- `action_date`: DateField (when action occurred)
- `jodi_column`: Integer (first column for multi-column bets)
- `jodi_type`: Integer (5, 7, 12 for JODI; 6, 7, 9 for JODI_PANEL)
- `is_undone`: Boolean (tracks if action was undone)
- `status`: ACTIVE, UNDONE, PARTIAL_UNDONE, COMPLETED

**Undo Functionality**:
```python
def undo(self, undone_by_user=None):
    """Deletes all associated bets and marks as undone"""
    deleted_count = self.bets.all().delete()[0]
    self.is_undone = True
    self.status = 'UNDONE'
    self.save()
    return True, f"Undone {deleted_count} bets"
```

---

## Bet Types & Number Selection

### 1. SINGLE BET
**Description**: Bet on a single 3-digit number
**Number Selection**: User clicks "+" button next to any number in the grid
**Numbers**: Any number from ALL_COLUMN_DATA (220 numbers total)
**UI Flow**:
```
User clicks + button → Modal opens → Enters amount → Places bet
```

### 2. SP (Single Panna) - 120 Numbers
**Description**: First 12 rows from each column (rows A-L)
**Number Selection Logic**:
```python
def get_sp_numbers():
    sp_numbers = []
    for col in ALL_COLUMN_DATA:  # 10 columns
        sp_numbers.extend([str(num) for num in col[0:12]])  # First 12
    return sp_numbers  # Returns 120 numbers
```
**Column-based SP**: User can select specific columns (1-10)
```python
# Multi-column SP example
columns = [1, 3, 5]  # User selects columns
sp_numbers_multi = []
for column in columns:
    column_index = int(column) - 1
    column_data = ALL_COLUMN_DATA[column_index]
    sp_from_column = [str(n) for n in column_data[0:12]]
    sp_numbers_multi.extend(sp_from_column)
# Remove duplicates
sp_numbers_multi = sorted(list(set(sp_numbers_multi)))
```

### 3. DP (Double Panna) - 100 Numbers
**Description**: Rows 13-22 from each column (rows M-V)
**Number Selection Logic**:
```python
def get_dp_numbers():
    dp_numbers = []
    for col in ALL_COLUMN_DATA:  # 10 columns
        dp_numbers.extend([str(num) for num in col[12:22]])  # Positions 12-21
    return dp_numbers  # Returns 100 numbers
```
**Column-based DP**: Same multi-column logic as SP

### 4. JODI VAGAR (Column-based betting)
**Description**: Predefined number sets per column with 3 types
**Jodi Vagar Numbers** (JODI_VAGAR_NUMBERS dictionary):
```python
JODI_VAGAR_NUMBERS = {
    1: [137, 146, 470, 579, 380, 119, 155, 227, 335, 399, 588, 669],
    2: [147, 246, 480, 138, 570, 228, 255, 336, 499, 688, 660, 200],
    # ... columns 3-10
}
```
**Three Types**:
1. **Jodi Vagar 5**: First 5 numbers from column
   ```python
   numbers = JODI_VAGAR_NUMBERS[column][:5]
   ```
2. **Jodi Vagar DP 7**: Last 7 numbers from column
   ```python
   numbers = JODI_VAGAR_NUMBERS[column][-7:]
   ```
3. **Jodi Vagar 12**: All 12 numbers from column
   ```python
   numbers = JODI_VAGAR_NUMBERS[column]  # All 12
   ```

**Multi-Column Support**: User can select multiple columns (1-10)
```python
# Example: Jodi Vagar 12 on columns 1, 3, 5
columns = [1, 3, 5]
jodi_type = 12
numbers = []
for column in columns:
    all_jodi_numbers = JODI_VAGAR_NUMBERS[column]
    numbers.extend([str(n) for n in all_jodi_numbers])
numbers = sorted(list(set(numbers)))  # Remove duplicates
```

### 5. DADAR - 10 Numbers
**Description**: Fixed set of 10 Dadar numbers
**Number Selection**:
```python
DADAR_NUMBERS = {
    1: [678], 2: [345], 3: [120], 4: [789], 5: [456],
    6: [123], 7: [890], 8: [567], 9: [234], 10: [190]
}
# All Dadar numbers: [678, 345, 120, 789, 456, 123, 890, 567, 234, 190]
```

### 6. EKI - 10 Numbers (Odd Pattern)
**Description**: Numbers with odd-digit patterns
**Numbers**: [137, 135, 139, 157, 159, 179, 357, 359, 379, 579]
```python
EKI_BEKI_NUMBERS = {
    'EKI': [137, 135, 139, 157, 159, 179, 357, 359, 379, 579],
}
```

### 7. BEKI - 10 Numbers (Even Pattern)
**Description**: Numbers with even-digit patterns
**Numbers**: [246, 248, 240, 268, 260, 280, 468, 460, 480, 680]
```python
EKI_BEKI_NUMBERS = {
    'BEKI': [246, 248, 240, 268, 260, 280, 468, 460, 480, 680],
}
```

### 8. ABR CUT - Column-based (9 numbers each)
**Description**: 9 specific numbers per column
**ABR_CUT_NUMBERS** (10 columns):
```python
ABR_CUT_NUMBERS = {
    1: [128, 146, 236, 245, 290, 380, 470, 489, 560],
    2: [129, 138, 147, 156, 237, 390, 570, 589, 679],
    # ... columns 3-10 (9 numbers each)
}
```
**Multi-Column Support**: User can select multiple columns
```python
columns = [1, 4, 7]  # User selection
numbers = []
for column in columns:
    numbers.extend(get_abr_cut_numbers(column))
numbers = sorted(list(set(numbers)))  # Deduplicate
```

### 9. JODI PANEL - Column-based (6/7/9 numbers)
**Description**: First N numbers from predefined panel sets
**JODI_PANEL_NUMBERS**:
```python
JODI_PANEL_NUMBERS = {
    1: [128, 236, 290, 560, 489, 245, 678, 344, 100],
    2: [129, 589, 679, 237, 390, 150, 345, 778, 110],
    # ... columns 3-10 (9 numbers each)
}
```
**Three Panel Types**:
1. **Panel 6**: First 6 numbers
   ```python
   numbers = JODI_PANEL_NUMBERS[column][:6]
   ```
2. **Panel 7**: First 7 numbers
   ```python
   numbers = JODI_PANEL_NUMBERS[column][:7]
   ```
3. **Panel 9**: All 9 numbers
   ```python
   numbers = JODI_PANEL_NUMBERS[column]  # All 9
   ```

### 10. MOTAR - Generated Numbers
**Description**: Generate 3-digit numbers from 4-10 digit input
**Algorithm** (Custom Order: 1<2<3<4<5<6<7<8<9<0):
```python
def generate_three_digit_numbers(digits_string):
    """
    Rules:
    - Custom order: 1 < 2 < 3 < 4 < 5 < 6 < 7 < 8 < 9 < 0
    - Pattern: a < b < c (strictly increasing)
    - 0 can only appear at position c (last)
    - Digits can repeat
    """
    order_map = {'1': 1, '2': 2, '3': 3, '4': 4, '5': 5, 
                 '6': 6, '7': 7, '8': 8, '9': 9, '0': 10}
    
    available_digits = list(set(digits_string))
    valid_numbers = []
    
    for a in available_digits:
        for b in available_digits:
            for c in available_digits:
                # 0 can only be at position c
                if a == '0' or b == '0':
                    continue
                # Check strictly increasing: a < b < c
                if order_map[a] < order_map[b] < order_map[c]:
                    number = a + b + c
                    valid_numbers.append(number)
    
    return sorted(valid_numbers)
```
**Example**:
```
Input: "4789"
Output: [479, 489, 490, 789, 780, 890] (numbers following rules)
```

### 11. COMMON PANA (36 or 56)
**Description**: Find all numbers containing a specific digit

#### Common Pana 36 (SP only)
```python
def find_sp_numbers_with_digit(digit):
    """Search only in SP numbers (first 12 from each column)"""
    digit_str = str(digit)
    sp_numbers_with_digit = []
    
    for column in ALL_COLUMN_DATA:  # 10 columns
        sp_numbers = column[0:12]  # First 12 (SP)
        for num in sp_numbers:
            if digit_str in str(num):
                sp_numbers_with_digit.append(str(num))
    
    return sorted(list(set(sp_numbers_with_digit)))
```
**Example**: Digit "4" in SP → Returns all SP numbers containing "4"

#### Common Pana 56 (SP + DP)
```python
def find_sp_dp_numbers_with_digit(digit):
    """Search in SP + DP numbers (first 22 rows from each column)"""
    digit_str = str(digit)
    sp_dp_numbers_with_digit = []
    
    for column in ALL_COLUMN_DATA:
        sp_dp_numbers = column[0:22]  # First 22 (SP + DP)
        for num in sp_dp_numbers:
            if digit_str in str(num):
                sp_dp_numbers_with_digit.append(str(num))
    
    return sorted(list(set(sp_dp_numbers_with_digit)))
```

### 12. SET PANA (Family Groups)
**Description**: Bet on all numbers in a family group (G1-G35)
**Family Groups** (35 groups, 4-8 numbers each):
```python
Family_Pana_numbers = {
    'G1': [678, 123, 137, 268, 236, 178, 128, 367],  # 8 numbers
    'G2': [345, 890, 390, 458, 480, 359, 589, 340],  # 8 numbers
    'G3': [120, 567, 157, 260, 256, 170, 670, 125],  # 8 numbers
    # ... G4-G30 (mostly 8 numbers)
    'G31': [227, 777, 277, 222],  # 4 numbers
    'G32': [499, 444, 449, 999],  # 4 numbers
    'G33': [166, 111, 116, 666],  # 4 numbers
    'G34': [338, 888, 388, 333],  # 4 numbers
    'G35': [500, 555, 550, 0]     # 4 numbers (includes '000')
}
```
**Selection Logic**:
```python
def find_family_group_by_number(number):
    """User enters any number from family, system finds entire group"""
    number_int = int(number)
    
    for family_name, family_numbers in Family_Pana_numbers.items():
        if number_int in family_numbers:
            return family_name, family_numbers
    
    return None, None
```
**Example**: User enters "156" → System finds G17: [156, 110, 660, 160, 566, 115]

### 13. COLUMN BET
**Description**: Bet directly on column number (1-10)
**Selection**: User selects one or more columns
**Storage**: 
- `bet_type = 'COLUMN'`
- `number = str(column)`  # e.g., "1", "5", "10"
- `column_number = column`  # Integer

---

## API Endpoints

### Authentication
- **Login**: `POST /login/` (username/email + password)
- **Logout**: `GET /logout/`

### Bet Placement
1. **Single Bet**
   ```
   POST /place-bet/
   Body: {
       "number": "137",
       "amount": 10,
       "bazar": "SRIDEVI_OPEN",
       "date": "2025-11-23"
   }
   Response: {
       "success": true,
       "bet_id": 123,
       "number": "137",
       "amount": "10.00"
   }
   ```

2. **Bulk Bet** (SP, DP, JODI, DADAR, etc.)
   ```
   POST /place-bulk-bet/
   Body: {
       "type": "JODI",           // SP, DP, JODI, DADAR, EKI, BEKI, ABR_CUT, JODI_PANEL
       "amount": 5,
       "bazar": "SRIDEVI_OPEN",
       "date": "2025-11-23",
       "columns": [1, 3, 5],     // For column-based bets
       "jodi_type": 12,          // For JODI: 5, 7, or 12
       "panel_type": 9           // For JODI_PANEL: 6, 7, or 9
   }
   Response: {
       "success": true,
       "message": "120 bets placed successfully",
       "bulk_action_id": 45,
       "total_bets": 120,
       "bets": [
           {"id": 124, "number": "128", "amount": "5.00"},
           ...
       ]
   }
   ```

3. **Motar Bet**
   ```
   POST /place-motar-bet/
   Body: {
       "digits": "4789",
       "amount": 10,
       "bazar": "SRIDEVI_OPEN",
       "date": "2025-11-23"
   }
   Response: {
       "success": true,
       "total_bets": 6,
       "bets": [...],
       "digits": "4789",
       "bulk_action_id": 46
   }
   ```

4. **Common Pana Bet**
   ```
   POST /place-comman-pana-bet/
   Body: {
       "digit": 4,
       "amount": 5,
       "type": "56",  // "36" or "56"
       "bazar": "SRIDEVI_OPEN",
       "date": "2025-11-23"
   }
   Response: {
       "success": true,
       "total_bets": 42,
       "digit": "4",
       "type": "56"
   }
   ```

5. **Set Pana Bet**
   ```
   POST /place-set-pana-bet/
   Body: {
       "number": 156,
       "amount": 10,
       "bazar": "SRIDEVI_OPEN",
       "date": "2025-11-23"
   }
   Response: {
       "success": true,
       "total_bets": 6,
       "family_name": "G17",
       "family_numbers": ["156", "110", "660", "160", "566", "115"]
   }
   ```

6. **Column Bet**
   ```
   POST /place-column-bet/
   Body: {
       "column": 3,
       "amount": 20,
       "bazar": "SRIDEVI_OPEN",
       "date": "2025-11-23"
   }
   Response: {
       "success": true,
       "column": 3,
       "amount": 20
   }
   ```

### Bet Management
1. **Load Bets**
   ```
   GET /load-bets/?bazar=SRIDEVI_OPEN&date=2025-11-23
   Response: {
       "success": true,
       "bets": {
           "137": {
               "total": 25.50,
               "history": [
                   {"id": 1, "amount": 10, "created_at": "...", "bet_type": "SINGLE"},
                   {"id": 2, "amount": 15.50, "created_at": "...", "bet_type": "JODI"}
               ]
           },
           ...
       }
   }
   ```

2. **Delete Bet**
   ```
   POST /delete-bet/
   Body: {"bet_id": 123}
   Response: {"success": true}
   ```

3. **Undo Bulk Action**
   ```
   POST /undo-bulk-action/
   Body: {"bulk_action_id": 45}
   Response: {
       "success": true,
       "message": "Successfully deleted bulk action with 120 bets"
   }
   ```

4. **Get Bet Total**
   ```
   GET /get-bet-total/?bazar=SRIDEVI_OPEN&date=2025-11-23
   Response: {
       "success": true,
       "total_amount": 1250.50
   }
   ```

5. **Get All Bet Totals** (Real-time sync)
   ```
   GET /get-all-bet-totals/?bazar=SRIDEVI_OPEN&date=2025-11-23
   Response: {
       "success": true,
       "bet_totals": {
           "128": 15.00,
           "137": 25.50,
           "146": 10.00,
           ...
       }
   }
   ```

6. **Get Column Totals**
   ```
   GET /get-column-totals/?bazar=SRIDEVI_OPEN&date=2025-11-23
   Response: {
       "success": true,
       "column_totals": {
           "1": 50.00,
           "2": 30.00,
           ...
       }
   }
   ```

### History & Stats
1. **Get Bulk Action History**
   ```
   GET /get-bulk-action-history/?bazar=SRIDEVI_OPEN&date=2025-11-23
   Response: {
       "success": true,
       "count": 15,
       "history": [
           {
               "id": 45,
               "action_type": "JODI",
               "amount": "5.00",
               "total_bets": 12,
               "jodi_column": 1,
               "jodi_type": 12,
               "created_at": "...",
               "is_undone": false,
               "bazar": "SRIDEVI_OPEN"
           },
           ...
       ]
   }
   ```

2. **Get Last Bulk Action**
   ```
   GET /get-last-bulk-action/?bazar=SRIDEVI_OPEN&date=2025-11-23
   Response: {
       "success": true,
       "has_action": true,
       "action": {
           "id": 45,
           "type": "JODI",
           "amount": "5.00",
           "total_bets": 12,
           ...
       }
   }
   ```

3. **Database Storage Info**
   ```
   GET /get-database-storage/
   Response: {
       "success": true,
       "storage_used_mb": 245.67,
       "storage_total_mb": 1024,
       "percentage": 24.01,
       "database_type": "PostgreSQL (Aiven)"
   }
   ```

### Number Generation (Preview)
1. **Generate Motar Numbers** (Preview only)
   ```
   POST /generate-motar-numbers/
   Body: {"digits": "4789"}
   Response: {
       "success": true,
       "numbers": ["479", "489", "490", "789", "780", "890"],
       "count": 6
   }
   ```

2. **Find Common Pana Numbers** (Preview only)
   ```
   POST /find-comman-pana-numbers/
   Body: {"digit": 4, "type": "36"}
   Response: {
       "success": true,
       "numbers": ["147", "248", "346", ...],
       "count": 36,
       "type": "36"
   }
   ```

---

## Number Selection Logic

### ALL_COLUMN_DATA Structure
**Central Data Structure**: 10 columns × 22 rows = 220 numbers
```python
ALL_COLUMN_DATA = [
    # Column 1 (22 numbers)
    [128, 137, 146, 236, 245, 290, 380, 470, 489, 560, 579, 678,  # SP (12)
     100, 119, 155, 227, 335, 344, 399, 588, 669, 777],  # DP (10)
    
    # Column 2 (22 numbers)
    [129, 138, 147, 156, 237, 246, 345, 390, 480, 570, 589, 679,  # SP (12)
     110, 200, 228, 255, 336, 499, 660, 688, 778, 444],  # DP (10)
    
    # ... Columns 3-10 (same structure)
]
```

### Row Labels (A-V, 22 rows)
```python
row_labels = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L',  # SP
              'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V']  # DP
```

### Number Validation
```javascript
// All valid numbers from ALL_COLUMN_DATA
const validNumbers = new Set();
allColumnData.forEach(column => {
    column.forEach(num => {
        let numStr = String(num).padStart(3, '0');  // Pad to 3 digits
        validNumbers.add(numStr);
    });
});
// validNumbers.size === 220
```

### UI Grid Rendering
**Page 1 (SP)**: Rows 0-11 (A-L)
```javascript
function renderPage(1) {
    for (let row = 0; row <= 11; row++) {
        for (let col = 0; col < 10; col++) {
            const value = allColumnData[col][row];
            // Display value with + button
        }
    }
}
```

**Page 2 (DP)**: Rows 13-22 (M-V)
```javascript
function renderPage(2) {
    for (let row = 13; row <= 22; row++) {
        const dataIndex = row - 1;  // Adjust index
        for (let col = 0; col < 10; col++) {
            const value = allColumnData[col][dataIndex];
            // Display value with + button
        }
    }
}
```

---

## UI/UX Flow

### User Interaction Patterns

#### 1. Single Number Betting
```
1. User views grid (SP or DP page)
2. Clicks "+" button next to number (e.g., "137")
3. Modal opens with:
   - Number displayed ("Place a Bet on 137")
   - Amount selection (quick buttons: 1, 2, 2.5, 5 OR custom)
   - Confirm/Cancel buttons
4. User selects amount → Clicks "Place Bet"
5. AJAX request to /place-bet/
6. On success:
   - Bet total appears next to number in green
   - Toast notification
   - Total balance updated
```

#### 2. Bulk Betting (SP/DP)
```
1. User clicks "All SP" or "All DP" button
2. Modal opens with:
   - Option to select specific columns (checkboxes 1-10)
   - OR leave empty to bet on all
   - Amount selection
3. User selects amount → Clicks "Place Bet"
4. AJAX request to /place-bulk-bet/ with:
   - type: 'SP' or 'DP'
   - columns: [1, 3, 5] or null (all)
   - amount: 10
5. Server creates individual bets for each number
6. Returns bulk_action_id for undo
```

#### 3. Jodi Vagar Betting
```
1. User clicks "Jodi Vagar" button
2. Modal opens with:
   - Dropdown: Select Type (5, 7, or 12)
   - Column checkboxes (1-10)
   - "Select All Columns" checkbox
   - Amount selection
3. User selects:
   - Type: 12
   - Columns: [1, 5, 10]
   - Amount: 5
4. Clicks "Place Bet"
5. Server logic:
   - For each column (1, 5, 10):
     - Get all 12 numbers from JODI_VAGAR_NUMBERS[column]
   - Deduplicate numbers
   - Create bets for unique numbers
6. Returns bulk_action_id
```

#### 4. Motar Number Generation
```
1. User clicks "Motar" button
2. Modal opens with input field
3. User types "4789" (4-10 digits)
4. As user types (input event):
   - AJAX to /generate-motar-numbers/ (preview)
   - Numbers displayed: [479, 489, 490, 789, 780, 890]
   - Count shown: "6 numbers will be generated"
5. User enters amount → Clicks "Place Bet"
6. AJAX to /place-motar-bet/:
   - Server generates numbers using algorithm
   - Creates bets in single transaction
   - Returns bulk_action_id
7. Undo button shows "Undo Last Motar (6 bets)"
```

#### 5. Common Pana (36 or 56)
```
1. User clicks "Common Bet" button
2. Modal opens with:
   - Checkbox: Common Pana 36 (SP only)
   - Checkbox: Common Pana 56 (SP + DP)
   - Input field: Single digit (0-9)
3. User:
   - Checks "Common Pana 56"
   - Types "4"
4. As user types (input event):
   - AJAX to /find-comman-pana-numbers/ (preview)
   - Returns all SP+DP numbers containing "4"
   - Displays numbers with count
5. User enters amount → Clicks "Place Bet"
6. Server creates bets for all matching numbers
```

#### 6. Set Pana (Family Groups)
```
1. User clicks "Set Pana" button
2. Modal opens with input field
3. User types "156" (any number from a family)
4. As user types (input event):
   - Client-side lookup in Family_Pana_numbers
   - Finds family G17: [156, 110, 660, 160, 566, 115]
   - Displays family name and all numbers
   - Highlights entered number
5. User enters amount → Clicks "Place Bet"
6. Server creates bets for all 6 family numbers
```

#### 7. Quick Bet Entry (Excel-like)
```
1. User clicks "Quick Bet" button
2. Floating table appears (bottom-right) with:
   - Row | Number (3-digit) | Amount | Delete
   - Initially 2 rows
3. User workflow:
   - Row 1: Types "128" → Presses Enter → Types "10" → Enter
   - Row 2: Types "137" → Presses Enter → Types "15" → Enter
   - Auto-adds new row when typing in last row
4. Optional: "Use same amount for all" checkbox
   - When checked, first row's amount applies to all
   - Amount fields become read-only
5. User clicks "Place Bets"
6. Validates each row:
   - Number must be 3 digits
   - Number must exist in validNumbers set
   - Amount must be > 0
7. Places all bets sequentially
8. Shows success count
```

### State Management

#### Client-Side State (JavaScript)
```javascript
// Global state variables
let currentBazar = 'SRIDEVI_OPEN';     // Saved to localStorage
let currentDate = '2025-11-23';        // Current selection
let bets = {};                          // { "137": {total: 25.5, history: [...]} }
let currentPage = 1;                    // 1 = SP, 2 = DP
let lastBulkAction = null;              // For undo functionality
let lastMotarBets = [];                 // For Motar undo
let lastCommanPanaBets = [];            // For Common Pana undo
let spAmountLimit = null;               // Highlighting threshold
let dpAmountLimit = null;               // Highlighting threshold
```

#### localStorage Persistence
```javascript
// Bazar selection persists across sessions
localStorage.setItem('selectedBazar', currentBazar);
localStorage.setItem('spAmountLimit', spAmountLimit);
localStorage.setItem('dpAmountLimit', dpAmountLimit);
```

### Real-time Synchronization
**Multi-Device Support**: Polling every 10 seconds
```javascript
setInterval(async () => {
    await refreshAllBetTotals();  // GET /get-all-bet-totals/
    // Updates bet totals from database
    // Ensures consistency across devices
}, 10000);
```

### Undo Functionality
**Three Types of Undo**:

1. **Bulk Action Undo** (SP, DP, JODI, etc.)
   ```javascript
   // lastBulkAction = {id: 45, type: 'JODI', total_bets: 12}
   POST /undo-bulk-action/
   Body: {bulk_action_id: 45}
   // Deletes all 12 bets associated with bulk action
   ```

2. **Motar Bet Undo** (Tracked separately)
   ```javascript
   // lastMotarBets = [{bet_id: 1, number: "479"}, ...]
   // Sequentially delete each bet
   for (const bet of lastMotarBets) {
       await deleteBet(bet.bet_id, bet.number);
   }
   ```

3. **Common Pana Undo** (Tracked separately)
   ```javascript
   // lastCommanPanaBets = [{bet_id: 10, number: "147"}, ...]
   // Sequentially delete each bet
   for (const bet of lastCommanPanaBets) {
       await deleteBet(bet.bet_id, bet.number);
   }
   ```

### Amount Limits & Highlighting
**Purpose**: Visual warning when bet total exceeds threshold
```javascript
// User sets limits in UI
spAmountLimit = 50;  // Highlight SP numbers with total >= 50
dpAmountLimit = 100; // Highlight DP numbers with total >= 100

// Applied via CSS class
if (betTotal >= limit) {
    cell.classList.add('highlight-limit');  // Yellow background
}
```

---

## Migration Checklist

### Backend (Node.js/Next.js API Routes)

#### 1. Database Schema (Prisma/TypeORM)
- [ ] Create `User` model (username, email, password hash)
- [ ] Create `Bet` model with all fields:
  - user relation
  - number (string, 3 digits)
  - amount (decimal)
  - bazar (enum)
  - bet_date (date)
  - bet_type (enum with 14 types)
  - column_number (int, nullable)
  - sub_type (string, nullable)
  - bulk_action relation (nullable)
  - status (enum)
  - created_at, updated_at
  - Indexes: (user, bazar, bet_date), (user, number), (bet_type, column_number)
- [ ] Create `BulkBetAction` model:
  - user relation
  - action_type (enum)
  - amount, total_bets
  - bazar, action_date
  - jodi_column, jodi_type
  - columns_used (string)
  - is_undone, status
  - created_at, updated_at
- [ ] Add database migrations

#### 2. Authentication
- [ ] Implement JWT-based auth (or NextAuth.js)
- [ ] Login API: `POST /api/auth/login`
- [ ] Logout API: `POST /api/auth/logout`
- [ ] Session middleware for protected routes

#### 3. Number Constants
- [ ] Create `/lib/betting-constants.ts`:
  - ALL_COLUMN_DATA (10 columns × 22 rows)
  - JODI_VAGAR_NUMBERS (10 columns × 12 numbers)
  - DADAR_NUMBERS
  - EKI_BEKI_NUMBERS
  - ABR_CUT_NUMBERS (10 columns × 9 numbers)
  - JODI_PANEL_NUMBERS (10 columns × 9 numbers)
  - Family_Pana_numbers (35 groups)
- [ ] Export helper functions:
  - `getSPNumbers()`, `getDPNumbers()`
  - `getJodiVagarNumbers(column, type)`
  - `getAbrCutNumbers(column)`
  - `getJodiPanelNumbers(column, panelType)`
  - `findFamilyGroupByNumber(number)`

#### 4. Motar Algorithm
- [ ] Create `/lib/motar-generator.ts`:
  - `generateThreeDigitNumbers(digits: string): string[]`
  - Implement custom order logic (1<2<...<9<0)
  - Rules: 0 only at position c, strictly increasing

#### 5. Common Pana Logic
- [ ] Create `/lib/common-pana.ts`:
  - `findSPNumbersWithDigit(digit: number): string[]`
  - `findSPDPNumbersWithDigit(digit: number): string[]`

#### 6. API Routes (Next.js App Router)
- [ ] `POST /api/bets/place` - Single bet
- [ ] `POST /api/bets/place-bulk` - Bulk betting
- [ ] `POST /api/bets/place-motar` - Motar bets
- [ ] `POST /api/bets/place-common-pana` - Common Pana bets
- [ ] `POST /api/bets/place-set-pana` - Set Pana bets
- [ ] `POST /api/bets/place-column` - Column bets
- [ ] `GET /api/bets/load` - Load user bets (with bazar & date filters)
- [ ] `POST /api/bets/delete` - Delete single bet
- [ ] `POST /api/bets/undo-bulk` - Undo bulk action
- [ ] `GET /api/bets/total` - Get total amount
- [ ] `GET /api/bets/totals-all` - Get all bet totals (for sync)
- [ ] `GET /api/bets/column-totals` - Get column totals
- [ ] `GET /api/bets/history` - Get bulk action history
- [ ] `GET /api/bets/last-bulk-action` - Get last bulk action
- [ ] `POST /api/numbers/generate-motar` - Preview Motar numbers
- [ ] `POST /api/numbers/find-common-pana` - Preview Common Pana
- [ ] `GET /api/system/database-storage` - Storage info

#### 7. Database Transactions
- [ ] Implement transaction support for bulk operations
- [ ] Ensure atomicity for place-bulk-bet (all or nothing)

#### 8. CSRF Protection
- [ ] Implement CSRF token generation
- [ ] Validate CSRF token in POST requests
- [ ] OR use SameSite cookies + CORS

#### 9. Error Handling
- [ ] Standardized error responses
- [ ] Validation errors (Zod or Joi)
- [ ] Database errors
- [ ] Authentication errors

### Frontend (React/Next.js)

#### 1. UI Components
- [ ] `BettingGrid` - Main spreadsheet grid
  - Column headers (1-10) with totals
  - Row labels (A-V)
  - Number cells with + buttons
  - Bet total display (green text)
  - Pagination (SP/DP)
- [ ] `BetModal` - Universal betting modal
  - Tab switching (Place Bet / History)
  - Conditional forms (SP, DP, JODI, etc.)
  - Amount selection (quick buttons + custom)
  - Column selection checkboxes
  - Undo button
- [ ] `QuickBetTable` - Excel-like entry
  - Dynamic rows
  - Number validation (validNumbers set)
  - "Same amount" checkbox
  - Enter key navigation
- [ ] `HistoryModal` - Bulk action history
  - Excel-like table
  - Filter by bazar/date
  - Delete button per action
  - Stats (total records, amount, bets)
- [ ] `Sidebar` - Settings panel
  - Bazar selector (12 options)
  - Date selector (last 30 + next 7 days)
  - User info
  - Database storage progress bar
  - "Show all bet types" toggle
  - Logout button
- [ ] `Toast` - Notification system
  - Success, error, warning types
  - Auto-dismiss (3s)
  - Close button
- [ ] `Loader` - Loading overlay
  - Animated loader
  - Status text ("Loading...", "Placing bet...")
  - Full-screen backdrop

#### 2. State Management (Zustand/Redux)
- [ ] Create store with:
  - `currentBazar` (persisted)
  - `currentDate`
  - `bets` (object keyed by number)
  - `currentPage` (1 or 2)
  - `lastBulkAction`
  - `lastMotarBets`, `lastCommanPanaBets`
  - `spAmountLimit`, `dpAmountLimit` (persisted)
- [ ] Actions:
  - `setBazar(bazar)`
  - `setDate(date)`
  - `loadBets()`
  - `placeBet(number, amount)`
  - `placeBulkBet(...)`
  - `deleteBet(betId, number)`
  - `undoBulkAction()`

#### 3. API Client (axios/fetch)
- [ ] Create `/lib/api-client.ts`:
  - Centralized API calls
  - CSRF token handling
  - Error handling
  - Loading states

#### 4. Number Validation
- [ ] Build `validNumbers` Set from ALL_COLUMN_DATA
- [ ] Validate input in QuickBetTable
- [ ] Visual feedback (red border for invalid)

#### 5. Real-time Sync
- [ ] Implement polling (10s interval)
- [ ] Call `GET /api/bets/totals-all`
- [ ] Update bet totals in UI
- [ ] Handle conflicts gracefully

#### 6. Highlighting Logic
- [ ] Apply `.highlight-limit` class when `betTotal >= limit`
- [ ] Re-apply after:
  - Page change
  - Bet placed/deleted
  - Limit changed

#### 7. Multi-Column Selection
- [ ] "Select All Columns" checkbox
- [ ] Sync with individual checkboxes
- [ ] Visual feedback (border color change)

#### 8. Undo System
- [ ] Track undo state for 3 types:
  - Bulk actions (lastBulkAction)
  - Motar (lastMotarBets array)
  - Common Pana (lastCommanPanaBets array)
- [ ] Show/hide undo button based on type
- [ ] Update button text with bet count

#### 9. Date & Bazar Persistence
- [ ] Save `selectedBazar` to localStorage
- [ ] Load on mount
- [ ] Sync sidebar and header displays

#### 10. Motar Preview
- [ ] Input event handler
- [ ] Debounce API call (300ms)
- [ ] Display generated numbers
- [ ] Show count

#### 11. Common Pana Preview
- [ ] Input event handler
- [ ] Debounce API call (300ms)
- [ ] Display found numbers
- [ ] Show count
- [ ] Mutual exclusivity (36 vs 56 checkboxes)

#### 12. Set Pana Lookup
- [ ] Client-side lookup in Family_Pana_numbers
- [ ] Display family name
- [ ] Display all family numbers
- [ ] Highlight entered number

#### 13. Column Bet UI
- [ ] Column selection checkboxes
- [ ] Amount input
- [ ] Place bet on one or multiple columns
- [ ] Display column totals in grid headers

### Testing

#### Backend Tests
- [ ] Unit tests for:
  - Motar number generation
  - Common Pana search
  - Family group lookup
  - Get SP/DP numbers
- [ ] Integration tests for:
  - Place single bet
  - Place bulk bet (all types)
  - Delete bet
  - Undo bulk action
  - Load bets with filters
- [ ] Database tests:
  - Transaction rollback
  - Concurrent bet placement
  - Index performance

#### Frontend Tests
- [ ] Component tests:
  - BettingGrid rendering
  - BetModal interactions
  - QuickBetTable validation
  - Amount selection
- [ ] Integration tests:
  - Full betting flow (end-to-end)
  - Undo functionality
  - Multi-device sync simulation
  - Bazar/date switching

### Deployment

#### Database
- [ ] Set up PostgreSQL (Aiven or similar)
- [ ] Run migrations
- [ ] Configure connection pooling
- [ ] Set up backups

#### Next.js App
- [ ] Environment variables:
  - `DATABASE_URL`
  - `JWT_SECRET`
  - `NEXT_PUBLIC_API_URL`
- [ ] Build optimization
- [ ] Deploy to Vercel/Railway/Render
- [ ] Configure CORS

#### Monitoring
- [ ] Set up error tracking (Sentry)
- [ ] Database monitoring (query performance)
- [ ] User analytics (bet patterns)

---

## Critical Implementation Notes

### 1. Transaction Safety
All bulk betting operations MUST be wrapped in database transactions:
```typescript
await prisma.$transaction(async (tx) => {
    const bulkAction = await tx.bulkBetAction.create({...});
    for (const number of numbers) {
        await tx.bet.create({
            ...data,
            bulkActionId: bulkAction.id
        });
    }
});
```

### 2. Deduplication
When combining multiple columns, always deduplicate:
```typescript
const numbers = [...new Set(allNumbers)];  // Remove duplicates
```

### 3. Number Padding
Always pad numbers to 3 digits:
```typescript
const paddedNumber = String(num).padStart(3, '0');  // 0 → "000"
```

### 4. Date Handling
Use consistent date format (YYYY-MM-DD):
```typescript
const betDate = new Date(dateString).toISOString().split('T')[0];
```

### 5. Index Strategy
Critical indexes for performance:
- `(user, bazar, bet_date)` - Most common query
- `(user, number)` - For bet total calculation
- `(bet_type, column_number)` - For column filtering
- `(created_at)` - For sorting

### 6. Soft Delete
Never hard delete bets (for audit trail):
```typescript
bet.is_deleted = true;
bet.deleted_at = new Date();
await bet.save();
```

### 7. Amount Precision
Use Decimal type (not Float) for amounts:
```typescript
amount: Decimal  // Prisma: @db.Decimal(10, 2)
```

### 8. CSRF Protection
Include CSRF token in all POST requests:
```typescript
headers: {
    'X-CSRFToken': getCSRFToken(),
    'Content-Type': 'application/json'
}
```

---

## Key Differences from Current Django App

### What's Already in Next.js App
✅ Basic authentication (login/logout API routes)
✅ Prisma schema with User, Bet models
✅ Home page structure
✅ Some API routes (load, place, delete bets)

### What Needs Implementation
❌ Bulk betting endpoints (SP, DP, JODI, etc.)
❌ Motar generation algorithm
❌ Common Pana search logic
❌ Set Pana family groups
❌ Column betting
❌ Undo functionality
❌ Multi-column selection
❌ Real-time sync (polling)
❌ Quick Bet Entry table
❌ History modal
❌ Amount limits & highlighting
❌ All 220 numbers in ALL_COLUMN_DATA
❌ Complete JODI_VAGAR_NUMBERS mapping
❌ Complete Family_Pana_numbers mapping

---

## Conclusion

This betting system is a complex, multi-layered application with:
- **14 distinct bet types** ranging from simple single bets to algorithmic generation (Motar)
- **220 unique betting numbers** organized in a 10×22 grid
- **Column-based betting** with multi-selection support
- **Family group betting** (35 groups)
- **Advanced features**: Undo, real-time sync, limits, Excel-like quick entry
- **12 bazars × multiple dates** = high data volume

The Django implementation is production-ready with:
- Proper indexing for performance
- Transaction safety for bulk operations
- CSRF protection
- Soft deletes for audit trail
- Multi-device synchronization

**Migration Priority**:
1. Core data models (User, Bet, BulkBetAction)
2. Number constants and helper functions
3. Single bet placement (simplest)
4. Bulk betting (SP, DP, JODI) - most used
5. Advanced features (Motar, Common Pana, Set Pana)
6. UI components (grid, modals, quick entry)
7. Real-time sync and undo
8. Polish (highlighting, limits, history modal)

This document should serve as the single source of truth for understanding and replicating the betting system in Node.js/Next.js.
