"""
Helper functions for viewing database contents during tests.
"""
from sqlalchemy.orm import Session
from models.database import Park, User, Equipment, Image, Review, ParkEquipment, Event
from typing import Optional


def print_table_contents(db: Session, table_name: str, limit: Optional[int] = None):
    """
    Print table contents during tests for debugging.
    
    Usage in tests:
        from tests.test_helpers import print_table_contents
        
        def test_something(db_session):
            # ... your test code ...
            print_table_contents(db_session, 'parks')
    """
    table_map = {
        'parks': Park,
        'users': User,
        'equipment': Equipment,
        'images': Image,
        'reviews': Review,
        'park_equipment': ParkEquipment,
        'events': Event,
    }
    
    if table_name.lower() not in table_map:
        print(f"Unknown table: {table_name}")
        print(f"Available tables: {', '.join(table_map.keys())}")
        return
    
    model = table_map[table_name.lower()]
    query = db.query(model)
    
    if limit:
        query = query.limit(limit)
    
    data = query.all()
    
    if not data:
        print(f"\n{table_name}: No records found")
        return
    
    print(f"\n{'='*80}")
    print(f"{table_name.upper()} ({len(data)} records)")
    print('='*80)
    
    # Print header
    if hasattr(data[0], '__table__'):
        columns = [col.name for col in data[0].__table__.columns]
        print(" | ".join(f"{col:20}" for col in columns))
        print("-" * 80)
        
        # Print rows
        for row in data:
            values = []
            for col in columns:
                val = getattr(row, col, None)
                if val is None:
                    val = "NULL"
                elif isinstance(val, str) and len(val) > 20:
                    val = val[:17] + "..."
                else:
                    val = str(val)
                values.append(f"{val:20}")
            print(" | ".join(values))
    
    print("="*80)


def print_all_tables_summary(db: Session):
    """Print a summary of all tables with record counts."""
    tables = {
        'parks': Park,
        'users': User,
        'equipment': Equipment,
        'images': Image,
        'reviews': Review,
        'park_equipment': ParkEquipment,
        'events': Event,
    }
    
    print("\n" + "="*80)
    print("DATABASE SUMMARY")
    print("="*80)
    
    for name, model in tables.items():
        count = db.query(model).count()
        print(f"{name:20} : {count:5} records")
    
    print("="*80)

