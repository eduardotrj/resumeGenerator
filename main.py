import sys
import os
from db.db import init_db


# Add current directory to Python path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from generators.resume_generator import generate_resume_and_cover_letter, test_llm_json


def main():
    """Main entry point - launches the GUI"""
    # Initialize the database
    init_db()

    try:
        print("🚀 Launching Resume Generator GUI...")
        from view import ResumeGeneratorGUI
        import tkinter as tk

        # Create and run GUI
        root = tk.Tk()
        app = ResumeGeneratorGUI(root)
        root.mainloop()

    except ImportError as e:
        print(f"❌ Error importing GUI: {e}")
        print("Make sure all required dependencies are installed")
    except Exception as e:
        print(f"💥 Error launching application: {e}")


if __name__ == "__main__":
    main()
