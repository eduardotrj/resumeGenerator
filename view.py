import tkinter as tk
from tkinter import ttk, scrolledtext
from tkinter import messagebox
import threading
import os
from generators.resume_generator import generate_resume_and_cover_letter  # , test_llm_json


class ResumeGeneratorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Resume Generator")
        self.root.geometry("900x700")
        self.root.resizable(True, True)

        # Variables to store form data
        self.company_name = tk.StringVar()
        self.language_choice = tk.StringVar(value="English")
        self.country_code = tk.StringVar(value="UK")
        self.city = tk.StringVar(value="London")

        self.create_widgets()

    def create_widgets(self):
        # Main frame with padding
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configure grid weights for responsive design
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(6, weight=1)

        # Title
        title_label = ttk.Label(main_frame, text="Resume Work Experience & Skills Adapter",
                                font=("Arial", 14, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 10))

        # Info label
        info_label = ttk.Label(main_frame,
                               text="Generates JSON, TXT, and HTML resumes with adapted work experience and skills",
                               font=("Arial", 10),
                               foreground="gray")
        info_label.grid(row=1, column=0, columnspan=2, pady=(0, 15))

        # Company Name Input
        ttk.Label(main_frame, text="Company Name:", font=("Arial", 12)).grid(
            row=2, column=0, sticky=tk.W, pady=(0, 5)
        )

        company_entry = ttk.Entry(
            main_frame,
            textvariable=self.company_name,
            font=("Arial", 11),
            width=40
        )
        company_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=(0, 15))

        # Location Frame (City and Country Code)
        location_frame = ttk.LabelFrame(main_frame, text="Location Information", padding="10")
        location_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))
        location_frame.columnconfigure(1, weight=1)
        location_frame.columnconfigure(3, weight=1)

        # City Input
        ttk.Label(location_frame, text="City:", font=("Arial", 11)).grid(
            row=0, column=0, sticky=tk.W, padx=(0, 10)
        )

        city_entry = ttk.Entry(
            location_frame,
            textvariable=self.city,
            font=("Arial", 11),
            width=25
        )
        city_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 20))

        # Country Code Input
        ttk.Label(location_frame, text="Country Code:", font=("Arial", 11)).grid(
            row=0, column=2, sticky=tk.W, padx=(0, 10)
        )

        country_entry = ttk.Entry(
            location_frame,
            textvariable=self.country_code,
            font=("Arial", 11),
            width=10
        )
        country_entry.grid(row=0, column=3, sticky=tk.W)

        # Helper text for location
        location_help = ttk.Label(location_frame,
                                 text="Example: City: 'London', Country Code: 'UK' or 'GB'",
                                 font=("Arial", 9),
                                 foreground="gray")
        location_help.grid(row=1, column=0, columnspan=4, sticky=tk.W, pady=(5, 0))

        # Language Selection
        ttk.Label(main_frame, text="Language:", font=("Arial", 12)).grid(
            row=4, column=0, sticky=tk.W, pady=(0, 5)
        )

        language_frame = ttk.Frame(main_frame)
        language_frame.grid(row=4, column=1, sticky=tk.W, pady=(0, 15))

        languages = ["English", "Spanish", "German"]
        for lang in languages:
            ttk.Radiobutton(
                language_frame,
                text=lang,
                variable=self.language_choice,
                value=lang,
                command=self.on_language_change
            ).pack(side=tk.LEFT, padx=(0, 20))

        # Job Offer Input (Large text area)
        ttk.Label(main_frame, text="Job Offer Description:", font=("Arial", 12)).grid(
            row=5, column=0, sticky=(tk.W, tk.N), pady=(0, 5)
        )

        self.job_offer_text = scrolledtext.ScrolledText(
            main_frame,
            width=60,
            height=12,
            font=("Arial", 10),
            wrap=tk.WORD
        )
        self.job_offer_text.grid(row=6, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 15))

        # Buttons Frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=7, column=0, columnspan=2, pady=(20, 0))

        # Generate Resume Button
        ttk.Button(
            button_frame,
            text="Generate Resume (JSON + TXT + HTML)",
            command=self.generate_resume,
            style="Accent.TButton"
        ).pack(side=tk.LEFT, padx=(0, 10))

        # Clear Form Button
        ttk.Button(
            button_frame,
            text="Clear Form",
            command=self.clear_form
        ).pack(side=tk.LEFT, padx=(0, 10))

        # Exit Button
        ttk.Button(
            button_frame,
            text="Exit",
            command=self.root.quit
        ).pack(side=tk.LEFT)

    def on_language_change(self):
        """Handle language selection change"""
        selected_lang = self.language_choice.get()
        print(f"Language selected: {selected_lang}")

    def generate_resume(self):
        """Handle resume generation"""
        company = self.company_name.get().strip()
        job_offer = self.job_offer_text.get("1.0", tk.END).strip()
        language = self.language_choice.get()
        city = self.city.get().strip()
        country_code = self.country_code.get().strip()

        # Basic validation
        if not company:
            messagebox.showwarning("Missing Information", "Please enter a company name.")
            return

        if not job_offer:
            messagebox.showwarning("Missing Information", "Please enter a job offer description.")
            return

        # Prepare the form data dictionary
        form_data = {
            "company_name": company,
            "job_offer": job_offer,
            "language": language,
            "city": city,
            "country_code": country_code
        }

        # Show progress message
        progress_window = tk.Toplevel(self.root)
        progress_window.title("Generating Documents...")
        progress_window.geometry("400x100")
        progress_window.transient(self.root)
        progress_window.grab_set()

        progress_label = ttk.Label(progress_window, text="Generating resume and cover letter...\nThis may take a few moments.")
        progress_label.pack(expand=True)

        progress_bar = ttk.Progressbar(progress_window, mode='indeterminate')
        progress_bar.pack(fill=tk.X, padx=20, pady=10)
        progress_bar.start()

        def generate_in_background():
            """Run the generation in a separate thread"""
            try:
                result = generate_resume_and_cover_letter(form_data)

                # Update UI in main thread
                self.root.after(0, lambda: self.handle_generation_result(result, progress_window))

            except Exception as e:
                error_result = {
                    'status': 'error',
                    'message': f'Unexpected error: {str(e)}'
                }
                self.root.after(0, lambda: self.handle_generation_result(error_result, progress_window))

        # Start generation in background thread
        thread = threading.Thread(target=generate_in_background)
        thread.daemon = True
        thread.start()

    def handle_generation_result(self, result, progress_window):
        """Handle the result of resume generation"""
        # Close progress window
        progress_window.destroy()

        if result['status'] == 'success':
            # Show success message with file paths
            files_list = "\n".join([f"• {os.path.basename(f)}" for f in result.get('files_created', [])])

            message = f"{result['message']}\n\nFiles created:\n{files_list}"

            # Add HTML file info if available
            if result.get('resume_html_file'):
                message += f"\n\n📄 HTML Resume: {os.path.basename(result['resume_html_file'])}"

            # Show success dialog with option to open files
            response = messagebox.askyesno(
                "Success!",
                f"{message}\n\nWould you like to open the output folder?",
                icon='question'
            )

            if response:
                # Open the outputs folder
                import subprocess
                import platform

                output_dir = os.path.abspath("outputs")
                try:
                    if platform.system() == "Windows":
                        subprocess.run(["explorer", output_dir])
                    elif platform.system() == "Darwin":  # macOS
                        subprocess.run(["open", output_dir])
                    else:  # Linux
                        subprocess.run(["xdg-open", output_dir])
                except Exception as e:
                    messagebox.showinfo("Info", f"Output folder: {output_dir}")

            # Optionally open HTML file in browser
            if result.get('resume_html_file'):
                html_response = messagebox.askyesno(
                    "Open HTML Resume?",
                    "Would you like to view the HTML resume in your browser?",
                    icon='question'
                )

                if html_response:
                    import webbrowser
                    try:
                        webbrowser.open(f"file://{os.path.abspath(result['resume_html_file'])}")
                    except Exception as e:
                        messagebox.showerror("Error", f"Could not open HTML file: {e}")

        else:
            # Show error message
            messagebox.showerror("Error", result['message'])

    def clear_form(self):
        """Clear all form fields"""
        self.company_name.set("")
        self.job_offer_text.delete("1.0", tk.END)
        self.language_choice.set("English")
        self.city.set("")
        self.country_code.set("")

    def get_form_data(self):
        """Get current form data as a dictionary"""
        return {
            "company_name": self.company_name.get().strip(),
            "job_offer": self.job_offer_text.get("1.0", tk.END).strip(),
            "language": self.language_choice.get(),
            "city": self.city.get().strip(),
            "country_code": self.country_code.get().strip()
        }


def main():
    """Main function to run the GUI application"""
    root = tk.Tk()
    app = ResumeGeneratorGUI(root)

    # Center the window on screen
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
    y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
    root.geometry(f"+{x}+{y}")

    root.mainloop()


if __name__ == "__main__":
    main()
