try:
    from app.main import app
    print("✅ Full app imports successfully")
except Exception as e:
    print(f"❌ Error importing app: {e}")
    import traceback
    traceback.print_exc()
