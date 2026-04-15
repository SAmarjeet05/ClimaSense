"""
Migration script to add missing columns to realtime_weather_data table
This adds the new columns without losing existing data
"""
import sqlite3
import os

db_path = r"C:\Old Data\Amarjeet\AI-Based Climate Change Data Analysis System\Backend\climate.db"

if not os.path.exists(db_path):
    print(f"Database not found at {db_path}")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    print("=" * 80)
    print("DATABASE MIGRATION: Adding missing columns to realtime_weather_data")
    print("=" * 80)
    
    # Check current schema
    cursor.execute("PRAGMA table_info(realtime_weather_data)")
    columns = [row[1] for row in cursor.fetchall()]
    print(f"\nCurrent columns: {columns}")
    
    # Add missing columns if they don't exist
    missing_columns = []
    
    if "is_real_data" not in columns:
        print("\n✓ Adding column: is_real_data")
        cursor.execute("""
        ALTER TABLE realtime_weather_data 
        ADD COLUMN is_real_data INTEGER NOT NULL DEFAULT 1
        """)
        missing_columns.append("is_real_data")
    else:
        print("\n✓ Column is_real_data already exists")
    
    if "data_quality_notes" not in columns:
        print("✓ Adding column: data_quality_notes")
        cursor.execute("""
        ALTER TABLE realtime_weather_data 
        ADD COLUMN data_quality_notes VARCHAR(255)
        """)
        missing_columns.append("data_quality_notes")
    else:
        print("✓ Column data_quality_notes already exists")
    
    # Commit the changes
    conn.commit()
    
    # Verify the columns were added
    cursor.execute("PRAGMA table_info(realtime_weather_data)")
    updated_columns = [row[1] for row in cursor.fetchall()]
    print(f"\nUpdated columns: {updated_columns}")
    
    # Count existing records
    cursor.execute("SELECT COUNT(*) FROM realtime_weather_data")
    record_count = cursor.fetchone()[0]
    
    print(f"\n✓ Migration successful!")
    print(f"✓ Preserved {record_count} existing records")
    print(f"✓ New columns added: {', '.join(missing_columns)}")
    
    print("\n" + "=" * 80)
    print("SCHEMA UPDATE COMPLETE")
    print("=" * 80)
    print("\nNext steps:")
    print("1. Restart the FastAPI server")
    print("2. Data will now be saved properly to the database")
    print("3. New records will have is_real_data=1 when fetched via API")

except Exception as e:
    print(f"\n❌ Migration failed: {str(e)}")
    conn.rollback()
    exit(1)

finally:
    conn.close()
