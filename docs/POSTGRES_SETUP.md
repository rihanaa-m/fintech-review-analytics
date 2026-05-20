# PostgreSQL Setup (Task 3)

## 1. Install PostgreSQL

Download from https://www.postgresql.org/download/windows/ and note your `postgres` user password.

## 2. Create database

```sql
CREATE DATABASE bank_reviews;
```

Or in PowerShell: `createdb -U postgres bank_reviews`

## 3. Set connection URL

```powershell
$env:DATABASE_URL = "postgresql+psycopg2://postgres:YOUR_PASSWORD@localhost:5432/bank_reviews"
```

## 4. Load data

```powershell
python scripts/load_to_postgres.py
```

## 5. Verify

Run queries in `database/verification_queries.sql` or check `data/processed/db_verification.json`.
