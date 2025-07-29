import unittest
from unittest.mock import patch, MagicMock
import sys
import os
from main import main
import main
import main
from main import main as main_func

# Import the main function to test


class TestMain(unittest.TestCase):
    """Test cases for the main module"""

    def setUp(self):
        """Set up test fixtures before each test method"""
        # Store original sys.path to restore later
        self.original_path = sys.path.copy()

    def tearDown(self):
        """Clean up after each test method"""
        # Restore original sys.path
        sys.path[:] = self.original_path

    @patch('main.init_db')
    @patch('main.tk.Tk')
    @patch('main.ResumeGeneratorGUI')
    def test_main_successful_execution(self, mock_gui_class, mock_tk, mock_init_db):
        """Test successful execution of main function"""
        # Setup mocks
        mock_root = MagicMock()
        mock_tk.return_value = mock_root
        mock_gui_instance = MagicMock()
        mock_gui_class.return_value = mock_gui_instance

        # Execute main function
        main()

        # Verify database initialization was called
        mock_init_db.assert_called_once()

        # Verify Tkinter root was created
        mock_tk.assert_called_once()

        # Verify GUI was instantiated with root
        mock_gui_class.assert_called_once_with(mock_root)

        # Verify mainloop was started
        mock_root.mainloop.assert_called_once()

    @patch('main.init_db')
    @patch('builtins.print')
    def test_main_import_error_handling(self, mock_print, mock_init_db):
        """Test handling of ImportError when importing GUI components"""
        # Mock init_db to work normally
        mock_init_db.return_value = None

        # Mock the import to raise ImportError
        with patch('main.ResumeGeneratorGUI', side_effect=ImportError("Mock import error")):
            # Execute main function
            main()

            # Verify database initialization was still called
            mock_init_db.assert_called_once()

            # Verify error messages were printed
            mock_print.assert_any_call("🚀 Launching Resume Generator GUI...")
            mock_print.assert_any_call("❌ Error importing GUI: Mock import error")
            mock_print.assert_any_call("Make sure all required dependencies are installed")

    @patch('main.init_db')
    @patch('main.tk.Tk')
    @patch('builtins.print')
    def test_main_general_exception_handling(self, mock_print, mock_tk, mock_init_db):
        """Test handling of general exceptions during execution"""
        # Setup mocks
        mock_init_db.return_value = None
        mock_tk.side_effect = Exception("Mock general error")

        # Execute main function
        main()

        # Verify database initialization was called
        mock_init_db.assert_called_once()

        # Verify error messages were printed
        mock_print.assert_any_call("🚀 Launching Resume Generator GUI...")
        mock_print.assert_any_call("💥 Error launching application: Mock general error")

    @patch('main.init_db')
    @patch('main.tk.Tk')
    @patch('main.ResumeGeneratorGUI')
    def test_main_gui_instantiation_order(self, mock_gui_class, mock_tk, mock_init_db):
        """Test that components are instantiated in correct order"""
        # Setup mocks
        mock_root = MagicMock()
        mock_tk.return_value = mock_root
        mock_gui_instance = MagicMock()
        mock_gui_class.return_value = mock_gui_instance

        # Execute main function
        main()

        # Verify call order
        self.assertEqual(mock_init_db.call_count, 1)
        self.assertEqual(mock_tk.call_count, 1)
        self.assertEqual(mock_gui_class.call_count, 1)

        # Verify GUI was created after Tk root
        mock_tk.assert_called_before(mock_gui_class)

    def test_sys_path_modification(self):
        """Test that sys.path is correctly modified"""
        original_length = len(sys.path)

        # Import main module (this triggers the sys.path.append)

        # Verify sys.path was modified
        self.assertGreater(len(sys.path), original_length)

        # Verify the correct path was added
        expected_path = os.path.dirname(os.path.abspath(main.__file__))
        self.assertIn(expected_path, sys.path)

    @patch('main.init_db', side_effect=Exception("Database error"))
    @patch('builtins.print')
    def test_main_database_init_error(self, mock_print, mock_init_db):
        """Test handling of database initialization errors"""
        # Execute main function
        main()

        # Verify database initialization was attempted
        mock_init_db.assert_called_once()

        # Verify error was handled and printed
        mock_print.assert_any_call("💥 Error launching application: Database error")

    @patch('main.init_db')
    @patch('main.tk.Tk')
    @patch('main.ResumeGeneratorGUI')
    @patch('builtins.print')
    def test_main_prints_launch_message(self, mock_print, mock_gui_class, mock_tk, mock_init_db):
        """Test that launch message is printed"""
        # Setup mocks
        mock_root = MagicMock()
        mock_tk.return_value = mock_root
        mock_gui_instance = MagicMock()
        mock_gui_class.return_value = mock_gui_instance

        # Execute main function
        main()

        # Verify launch message was printed
        mock_print.assert_any_call("🚀 Launching Resume Generator GUI...")

    @patch('main.init_db')
    def test_main_tkinter_import_error(self, mock_init_db):
        """Test handling when tkinter import fails"""
        mock_init_db.return_value = None

        with patch('main.tk', side_effect=ImportError("No module named 'tkinter'")):
            with patch('builtins.print') as mock_print:
                main()

                # Verify error handling
                mock_print.assert_any_call("❌ Error importing GUI: No module named 'tkinter'")

    def test_module_level_imports(self):
        """Test that required modules can be imported"""
        # Test that main module imports work
        try:
            self.assertTrue(callable(main_func))
        except ImportError as e:
            self.fail(f"Failed to import main module: {e}")


if __name__ == '__main__':
    # Run the tests
    unittest.main()