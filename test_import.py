import sys
import traceback

try:
    print("Testing paper_generator import...")
    from src.output.paper_generator import PaperGenerator
    print("OK: paper_generator imported successfully")
    
    print("\nTesting gui_app import...")
    import gui_app
    print("OK: gui_app imported successfully")
    
except Exception as e:
    print(f"ERROR: {type(e).__name__}: {e}")
    traceback.print_exc()
