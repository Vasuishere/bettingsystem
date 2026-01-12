# Django → Next.js Migration Roadmap

## 📊 Current Architecture Analysis

### Django Models Inventory

| Model | Purpose | Fields | Dependencies |
|-------|---------|--------|--------------|
| `CustomUser` | User authentication | Extends AbstractUser (username, email, password, etc.) | Django auth system |
| `Bet` | Individual bet records | user, number, amount, bet_type, bazar, bet_date, status, bulk_action, column_number, etc. | CustomUser, BulkBetAction |
| `BulkBetAction` | Track bulk betting operations | user, action_type, amount, total_bets, bazar, action_date, status, etc. | CustomUser |

### Authentication Flow Analysis

```
┌─────────────────────────────────────────────────────────────────┐
│                    DJANGO AUTH FLOW                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1. Login Request (POST /)                                       │
│     ├── email + password                                         │
│     ├── authenticate(username=email, password)                   │
│     │   └── Falls back to: lookup by email, get username         │
│     ├── auth_login(request, user) → Creates session              │
│     └── Redirect to /home/                                       │
│                                                                  │
│  2. Session Management                                           │
│     ├── SESSION_ENGINE: 'cached_db'                              │
│     ├── SESSION_COOKIE_AGE: 1209600 (2 weeks)                    │
│     └── CSRF protection enabled                                  │
│                                                                  │
│  3. Protected Routes                                             │
│     ├── @login_required decorator                                │
│     └── Redirects to LOGIN_URL = '/'                             │
│                                                                  │
│  4. Logout (GET /logout/)                                        │
│     ├── auth_logout(request)                                     │
│     └── Redirect to '/'                                          │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### API Endpoints Mapping

| Django Endpoint | HTTP Method | Purpose | Next.js Route |
|-----------------|-------------|---------|---------------|
| `/` | GET/POST | Login page & auth | `app/api/auth/login/route.ts` |
| `/logout/` | GET | Logout | `app/api/auth/logout/route.ts` |
| `/home/` | GET | Home page (protected) | `app/(protected)/home/page.tsx` |
| `/place-bet/` | POST | Single bet | `app/api/bets/place/route.ts` |
| `/place-bulk-bet/` | POST | Bulk betting | `app/api/bets/bulk/route.ts` |
| `/load-bets/` | GET | Load user bets | `app/api/bets/route.ts` |
| `/delete-bet/` | POST | Delete single bet | `app/api/bets/[id]/route.ts` |
| `/undo-bulk-action/` | POST | Undo bulk action | `app/api/bulk-actions/undo/route.ts` |
| `/get-last-bulk-action/` | GET | Get last bulk action | `app/api/bulk-actions/last/route.ts` |
| `/master-delete-all-bets/` | POST | Delete all bets | `app/api/bets/master-delete/route.ts` |
| `/delete-bazar-bets/` | POST | Delete bazar bets | `app/api/bets/delete-bazar/route.ts` |
| `/get-total-bet-count/` | GET | Total bet count | `app/api/bets/count/route.ts` |
| `/generate-motar-numbers/` | POST | Generate Motar numbers | `app/api/numbers/motar/route.ts` |
| `/find-comman-pana-numbers/` | POST | Find Comman Pana | `app/api/numbers/comman-pana/route.ts` |
| `/place-motar-bet/` | POST | Place Motar bet | `app/api/bets/motar/route.ts` |
| `/place-comman-pana-bet/` | POST | Place Comman Pana bet | `app/api/bets/comman-pana/route.ts` |
| `/place-set-pana-bet/` | POST | Place Set Pana bet | `app/api/bets/set-pana/route.ts` |
| `/place-group-bet/` | POST | Place Group bet | `app/api/bets/group/route.ts` |
| `/get-bet-summary/` | GET | Bet summary | `app/api/bets/summary/route.ts` |
| `/get-bet-total/` | GET | Bet total | `app/api/bets/total/route.ts` |
| `/get-all-bet-totals/` | GET | All bet totals | `app/api/bets/totals/route.ts` |
| `/get-bulk-action-history/` | GET | Bulk action history | `app/api/bulk-actions/history/route.ts` |
| `/get-database-storage/` | GET | DB storage info | `app/api/system/storage/route.ts` |
| `/place-column-bet/` | POST | Column bet | `app/api/bets/column/route.ts` |
| `/get-column-totals/` | GET | Column totals | `app/api/bets/column-totals/route.ts` |

---

## 🔐 Authentication Strategy for Next.js

### Recommended: Cookie-Based Sessions with Iron Session

**Why Cookie-Based (not JWT)?**
1. ✅ Matches Django's session model (easier migration)
2. ✅ HttpOnly cookies prevent XSS attacks
3. ✅ Server-side session validation
4. ✅ Easy logout (clear cookie)
5. ✅ Compatible with existing password hashes

### Password Compatibility

Django uses PBKDF2 by default:
```
pbkdf2_sha256$<iterations>$<salt>$<hash>
```

We'll use `@node-rs/argon2` or custom PBKDF2 verification to maintain compatibility.

---

## 🗄️ Database Schema (Prisma)

```prisma
// schema.prisma

generator client {
  provider = "prisma-client-js"
}

datasource db {
  provider = "postgresql"
  url      = env("DATABASE_URL")
}

model User {
  id          Int       @id @default(autoincrement())
  username    String    @unique
  email       String    @unique
  password    String    // Django PBKDF2 hash
  firstName   String?   @map("first_name")
  lastName    String?   @map("last_name")
  isStaff     Boolean   @default(false) @map("is_staff")
  isActive    Boolean   @default(true) @map("is_active")
  isSuperuser Boolean   @default(false) @map("is_superuser")
  dateJoined  DateTime  @default(now()) @map("date_joined")
  lastLogin   DateTime? @map("last_login")
  
  bets           Bet[]
  bulkActions    BulkBetAction[]
  deletedBets    Bet[]           @relation("DeletedBy")
  undoneBulkActions BulkBetAction[] @relation("UndoneBy")

  @@map("userbaseapp_customuser")
}

model Bet {
  id           Int       @id @default(autoincrement())
  userId       Int       @map("user_id")
  number       String
  amount       Decimal   @db.Decimal(10, 2)
  createdAt    DateTime  @default(now()) @map("created_at")
  updatedAt    DateTime  @updatedAt @map("updated_at")
  
  bazar        String    @default("SRIDEVI_OPEN")
  betDate      DateTime  @map("bet_date") @db.Date
  
  bulkActionId Int?      @map("bulk_action_id")
  betType      String    @default("SINGLE") @map("bet_type")
  columnNumber Int?      @map("column_number")
  subType      String?   @map("sub_type")
  familyGroup  String?   @map("family_group")
  inputDigits  String?   @map("input_digits")
  searchDigit  Int?      @map("search_digit")
  sessionId    String?   @map("session_id")
  status       String    @default("ACTIVE")
  notes        String?
  isDeleted    Boolean   @default(false) @map("is_deleted")
  deletedAt    DateTime? @map("deleted_at")
  deletedById  Int?      @map("deleted_by_id")

  user         User           @relation(fields: [userId], references: [id])
  bulkAction   BulkBetAction? @relation(fields: [bulkActionId], references: [id])
  deletedBy    User?          @relation("DeletedBy", fields: [deletedById], references: [id])

  @@index([userId, number])
  @@index([userId, createdAt(sort: Desc)])
  @@index([userId, betType])
  @@index([userId, bazar, betDate])
  @@map("userbaseapp_bet")
}

model BulkBetAction {
  id          Int       @id @default(autoincrement())
  userId      Int       @map("user_id")
  actionType  String    @map("action_type")
  amount      Decimal   @db.Decimal(10, 2)
  totalBets   Int       @default(0) @map("total_bets")
  totalAmount Decimal   @default(0) @db.Decimal(10, 2) @map("total_amount")
  
  bazar       String    @default("SRIDEVI_OPEN")
  actionDate  DateTime  @map("action_date") @db.Date
  
  jodiColumn  Int?      @map("jodi_column")
  jodiType    Int?      @map("jodi_type")
  columnsUsed String?   @map("columns_used")
  familyGroup String?   @map("family_group")
  familyNumbers String? @map("family_numbers")
  inputData   String?   @map("input_data")
  searchDigit Int?      @map("search_digit")
  
  createdAt   DateTime  @default(now()) @map("created_at")
  updatedAt   DateTime  @updatedAt @map("updated_at")
  
  status      String    @default("ACTIVE")
  isUndone    Boolean   @default(false) @map("is_undone")
  undoneAt    DateTime? @map("undone_at")
  undoneById  Int?      @map("undone_by_id")
  notes       String?
  isDeleted   Boolean   @default(false) @map("is_deleted")
  deletedAt   DateTime? @map("deleted_at")

  user        User      @relation(fields: [userId], references: [id])
  undoneBy    User?     @relation("UndoneBy", fields: [undoneById], references: [id])
  bets        Bet[]

  @@index([userId, createdAt(sort: Desc)])
  @@index([userId, actionType])
  @@index([userId, bazar, actionDate])
  @@map("userbaseapp_bulkbetaction")
}
```

---

## 📁 Next.js Project Structure

```
nextjs-betting-app/
├── app/
│   ├── (auth)/
│   │   ├── login/
│   │   │   └── page.tsx
│   │   └── layout.tsx
│   ├── (protected)/
│   │   ├── home/
│   │   │   └── page.tsx
│   │   └── layout.tsx
│   ├── api/
│   │   ├── auth/
│   │   │   ├── login/route.ts
│   │   │   ├── logout/route.ts
│   │   │   └── me/route.ts
│   │   ├── bets/
│   │   │   ├── route.ts              # GET: load bets
│   │   │   ├── place/route.ts        # POST: single bet
│   │   │   ├── bulk/route.ts         # POST: bulk bet
│   │   │   ├── [id]/route.ts         # DELETE: single bet
│   │   │   ├── motar/route.ts
│   │   │   ├── comman-pana/route.ts
│   │   │   ├── set-pana/route.ts
│   │   │   ├── group/route.ts
│   │   │   ├── column/route.ts
│   │   │   ├── summary/route.ts
│   │   │   ├── total/route.ts
│   │   │   ├── totals/route.ts
│   │   │   ├── column-totals/route.ts
│   │   │   ├── count/route.ts
│   │   │   ├── master-delete/route.ts
│   │   │   └── delete-bazar/route.ts
│   │   ├── bulk-actions/
│   │   │   ├── undo/route.ts
│   │   │   ├── last/route.ts
│   │   │   └── history/route.ts
│   │   ├── numbers/
│   │   │   ├── motar/route.ts
│   │   │   └── comman-pana/route.ts
│   │   └── system/
│   │       └── storage/route.ts
│   ├── layout.tsx
│   └── page.tsx
├── lib/
│   ├── auth/
│   │   ├── session.ts           # Iron session config
│   │   ├── password.ts          # Django password verification
│   │   └── middleware.ts        # Auth middleware
│   ├── db/
│   │   └── prisma.ts            # Prisma client
│   ├── betting/
│   │   ├── constants.ts         # All number mappings
│   │   ├── sp-dp.ts
│   │   ├── jodi-vagar.ts
│   │   ├── dadar.ts
│   │   ├── eki-beki.ts
│   │   ├── abr-cut.ts
│   │   ├── jodi-panel.ts
│   │   ├── motar.ts
│   │   ├── comman-pana.ts
│   │   ├── set-pana.ts
│   │   └── group.ts
│   └── utils/
│       └── api-response.ts
├── components/
│   ├── ui/
│   ├── auth/
│   │   └── login-form.tsx
│   └── betting/
│       ├── spreadsheet.tsx
│       ├── bet-controls.tsx
│       └── toast.tsx
├── hooks/
│   ├── use-auth.ts
│   └── use-bets.ts
├── middleware.ts                # Route protection
├── prisma/
│   └── schema.prisma
├── package.json
├── tsconfig.json
├── tailwind.config.ts
└── .env.local
```

---

## 🚀 Migration Phases

### Phase 1: Foundation (Week 1)
- [x] Analyze Django codebase ✅
- [ ] Set up Next.js 15 project
- [ ] Configure Prisma with existing PostgreSQL
- [ ] Implement password verification (Django compatibility)
- [ ] Create auth routes (login/logout/me)
- [ ] Set up Iron Session

### Phase 2: Core Business Logic (Week 2)
- [ ] Port all number mapping constants
- [ ] Implement betting calculation functions
- [ ] Create bet placement APIs
- [ ] Create bet loading/deletion APIs
- [ ] Implement bulk action APIs

### Phase 3: UI Migration (Week 3)
- [ ] Create login page
- [ ] Create home page with spreadsheet
- [ ] Wire up all button actions
- [ ] Implement toast notifications
- [ ] Add loading states

### Phase 4: Testing & Cutover (Week 4)
- [ ] Parallel run Django + Next.js
- [ ] Compare behavior on all flows
- [ ] Fix regressions
- [ ] Performance testing
- [ ] Final cutover

---

## 🔄 Critical Business Logic to Preserve

### 1. Number Mappings (MUST BE IDENTICAL)
```typescript
// ALL_COLUMN_DATA - 10 columns × 22 numbers each
// JODI_VAGAR_NUMBERS - 10 columns × 12 numbers each
// Family_Pana_numbers - G1-G35 families
// DADAR_NUMBERS - 10 numbers
// EKI_BEKI_NUMBERS - 10 numbers each
// ABR_CUT_NUMBERS - 10 columns × 9 numbers each
// JODI_PANEL_NUMBERS - 10 columns × 9 numbers each
```

### 2. Motar Number Generation Algorithm
```typescript
// Custom order: 1 < 2 < 3 < 4 < 5 < 6 < 7 < 8 < 9 < 0
// Pattern: a < b < c (strictly increasing)
// 0 can only appear at position c (last position)
```

### 3. Common Pana Logic
- Type 36: Search only in SP numbers (first 12 per column)
- Type 56: Search in SP + DP numbers (first 22 per column)

### 4. Set Pana Family Lookup
- Find family group (G1-G35) containing the input number
- Bet on all numbers in that family

---

## ⚠️ Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Password incompatibility | Use custom PBKDF2 verification matching Django |
| Session migration | Keep Django sessions valid during transition |
| Data loss | Read-only period during cutover |
| Number calculation errors | Unit tests with Django output as golden reference |
| Performance regression | Load test before cutover |

---

## 📋 Verification Checklist

### Authentication
- [ ] Login with existing user credentials
- [ ] Session persists across page refreshes
- [ ] Logout clears session
- [ ] Protected routes redirect to login

### Betting Operations
- [ ] Single bet placement
- [ ] SP bet (all/column specific)
- [ ] DP bet (all/column specific)
- [ ] Jodi Vagar bet (5/7/12 types)
- [ ] Dadar bet
- [ ] Eki/Beki bet
- [ ] ABR Cut bet
- [ ] Jodi Panel bet (6/7/9 types)
- [ ] Motar bet
- [ ] Common Pana bet (36/56)
- [ ] Set Pana bet
- [ ] Group bet
- [ ] Column bet

### Data Operations
- [ ] Load bets by bazar/date
- [ ] Delete single bet
- [ ] Undo bulk action
- [ ] Master delete
- [ ] Bazar delete
- [ ] Get totals

---

## 🏁 Success Criteria

1. **Zero data loss** during migration
2. **Identical behavior** for all betting calculations
3. **Seamless auth** for existing users
4. **Better performance** than Django
5. **No regressions** in any user flow
