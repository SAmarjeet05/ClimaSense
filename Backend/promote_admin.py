"""
Promote admin user to admin role
"""
import sqlite3
from pathlib import Path

db_path = Path('climate.db')
conn = sqlite3.connect(str(db_path))
cursor = conn.cursor()

# Get the admin user and promote them
cursor.execute('''
    UPDATE users 
    SET role = 'admin' 
    WHERE name = 'Phase4 Admin'
''')

# Verify the update
cursor.execute('SELECT id, name, email, role FROM users')
all_users = cursor.fetchall()

print('✅ All users in database:')
for user in all_users:
    role_marker = '👤 USER ' if user[3] == 'user' else '👨‍💼 ADMIN'
    print(f'  {role_marker}: ID={user[0]}, {user[1]} ({user[2]})')

conn.commit()
conn.close()
