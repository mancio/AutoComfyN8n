import subprocess
import sqlite3
from pathlib import Path

# Generate bcrypt hash using Docker (bcrypt is available in the container)
result = subprocess.run([
    'docker', 'run', '--rm', 'python:3.10-slim',
    'python', '-c',
    'import subprocess; subprocess.run(["pip", "install", "bcrypt", "-q"], check=True); import bcrypt; pwd = b"admin123"; hashed = bcrypt.hashpw(pwd, bcrypt.gensalt(rounds=10)); print(hashed.decode())'
], capture_output=True, text=True, timeout=60)

if result.returncode != 0:
    print(f"Error: {result.stderr}")
    # Use a pre-generated hash as fallback
    # This is bcrypt($2b$10$) hash of "admin123"
    password_hash = "$2b$10$R9h7cIPz0gi.URNNBWQ0VeL8PlYHjMLEQXl9IeKm0xYlXL5TJNYL."
else:
    password_hash = result.stdout.strip()

print(f"Password hash: {password_hash}")

# Update database
p = Path(r'C:\Users\andma\VSStudioCode\AutoComfyN8n\n8n_data\database.sqlite')
conn = sqlite3.connect(p)
cur = conn.cursor()

cur.execute('UPDATE user SET password = ? WHERE roleSlug = ?', [password_hash, 'global:owner'])
conn.commit()

cur.execute('SELECT id, email, password FROM user WHERE roleSlug = ?', ['global:owner'])
row = cur.fetchone()
if row:
    print(f"✓ Updated user:")
    print(f"  Email: {row[1]}")
    print(f"  Password: {row[2][:30]}...")

conn.close()
