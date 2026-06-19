"""Fix database schema mismatches with SQLAlchemy models.

Issues found:
1. products.status ENUM was lowercase (fixed)
2. users.status ENUM is lowercase ('active','banned') vs model uppercase ('ACTIVE','BANNED')
3. users table is missing is_admin column
"""
from sqlalchemy import create_engine, text
from app.core.settings import settings

engine = create_engine(settings.database_url, pool_pre_ping=True)

with engine.connect() as conn:
    print("=" * 60)
    print("1. Fix users.status ENUM (lowercase -> uppercase)")
    print("=" * 60)
    
    # Check current data
    result = conn.execute(text("SELECT id, nickname, status FROM users"))
    print("Before:")
    for row in result:
        print(f"  id={row[0]}, nickname={row[1]}, status={row[2]}")
    
    # ALTER TABLE to uppercase ENUM
    conn.execute(text(
        "ALTER TABLE users MODIFY COLUMN status "
        "ENUM('ACTIVE','BANNED') "
        "NOT NULL DEFAULT 'ACTIVE'"
    ))
    conn.commit()
    
    # Update existing data from lowercase to uppercase
    conn.execute(text("UPDATE users SET status = 'ACTIVE' WHERE status = 'active'"))
    conn.execute(text("UPDATE users SET status = 'BANNED' WHERE status = 'banned'"))
    conn.commit()
    
    result = conn.execute(text("SELECT id, nickname, status FROM users"))
    print("After:")
    for row in result:
        print(f"  id={row[0]}, nickname={row[1]}, status={row[2]}")
    
    print()
    print("=" * 60)
    print("2. Add missing is_admin column to users")
    print("=" * 60)
    
    # Check if column already exists
    result = conn.execute(text("SHOW COLUMNS FROM users LIKE 'is_admin'"))
    if result.fetchone():
        print("is_admin column already exists, skipping.")
    else:
        conn.execute(text(
            "ALTER TABLE users ADD COLUMN is_admin TINYINT(1) NOT NULL DEFAULT 0"
        ))
        conn.commit()
        print("Added is_admin column (TINYINT(1), default 0)")
    
    # Verify columns
    print()
    print("Final users table columns:")
    result = conn.execute(text("SHOW COLUMNS FROM users"))
    for row in result:
        print(f"  {row[0]:20s} {str(row[1]):30s} Default: {row[4]}")
    
    print()
    print("=" * 60)
    print("3. Verify products status")
    print("=" * 60)
    result = conn.execute(text("SELECT id, title, status FROM products"))
    for row in result:
        print(f"  id={row[0]}, title={row[1]}, status={row[2]}")

print()
print("All fixes applied!")
