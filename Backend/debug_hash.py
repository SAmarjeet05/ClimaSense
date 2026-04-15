from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

# Test password
test_password = "SecurePass123"
print(f"Password: {test_password}")
print(f"Length: {len(test_password)} bytes")

try:
    hashed = pwd_context.hash(test_password)
    print(f"✅ Hashed successfully: {hashed[:50]}...")
    
    # Test verify
    is_valid = pwd_context.verify(test_password, hashed)
    print(f"✅ Verify result: {is_valid}")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
