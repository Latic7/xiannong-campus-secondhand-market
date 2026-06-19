"""Fix lowercase status values in products table."""
from sqlalchemy import create_engine, text
from app.core.settings import settings

engine = create_engine(settings.database_url, pool_pre_ping=True)
with engine.connect() as conn:
    # 查看列定义
    result = conn.execute(text("SHOW COLUMNS FROM products LIKE 'status'"))
    for row in result:
        print(f"Column: {row}")

    # 查看当前数据
    result = conn.execute(text("SELECT id, title, status FROM products"))
    print("\nBefore fix:")
    for row in result:
        print(f"  id={row[0]}, title={row[1]}, status={row[2]}")

    # ALTER TABLE 修改 ENUM 列为大写值
    conn.execute(text(
        "ALTER TABLE products MODIFY COLUMN status "
        "ENUM('DRAFT','PENDING','PUBLISHED','REMOVED','SOLD') "
        "NOT NULL DEFAULT 'PENDING'"
    ))
    conn.commit()
    print("\nAltered ENUM column to uppercase values")

    # 修复现有数据
    result = conn.execute(
        text("UPDATE products SET status = 'PUBLISHED' WHERE status = 'published'")
    )
    conn.commit()
    print(f"Updated {result.rowcount} rows")

    # 验证
    result = conn.execute(text("SELECT id, title, status FROM products"))
    print("\nAfter fix:")
    for row in result:
        print(f"  id={row[0]}, title={row[1]}, status={row[2]}")
