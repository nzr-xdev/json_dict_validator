import customtkinter as ctk
from tkinter import filedialog, messagebox
from core import DataValidator
import json

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class DataValidatorGUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("JSON Data Validator")
        self.geometry("1000 x 650")

        self.validator = DataValidator()

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.sidebar = ctk.CTkFrame(self, width=250, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        
        self.logo_label = ctk.CTkLabel(self.sidebar, text="DataValidator v1.0", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        self.load_data_btn = ctk.CTkButton(self.sidebar, text="Load JSON Data", command=self._load_data_file)
        self.load_data_btn.grid(row=1, column=0, padx=20, pady=10)

        self.load_config_btn = ctk.CTkButton(self.sidebar, text="Load Config", command=self._load_config_file)
        self.load_config_btn.grid(row=2, column=0, padx=20, pady=10)

        self.run_btn = ctk.CTkButton(self.sidebar, text="RUN VALIDATION", fg_color="#2ecc71", hover_color="#27ae60", command=self._handle_run)
        self.run_btn.grid(row=3, column=0, padx=20, pady=(100, 20))

        self.main_content = ctk.CTkFrame(self, corner_radius=15)
        self.main_content.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        self.main_content.grid_rowconfigure(1, weight=1)
        self.main_content.grid_columnconfigure(0, weight=1)

        self.status_label = ctk.CTkLabel(self.main_content, text="Ready to scan", font=ctk.CTkFont(size=14))
        self.status_label.grid(row=0, column=0, padx=20, pady=(10, 0), sticky="w")

        self.result_box = ctk.CTkTextbox(self.main_content, font=ctk.CTkFont(family="Consolas", size=12))
        self.result_box.grid(row=1, column=0, padx=20, pady=20, sticky="nsew")

    def _load_data_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if file_path:
            print(f"Data selected: {file_path}")
            self.status_label.configure(text=f"Data: {file_path.split('/')[-1]}", text_color="white")

        self.path_selected_data = (file_path)

    def _load_config_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if file_path:
            print(f"Config selected: {file_path}")
            self.status_label.configure(text=f"Config: {file_path.split('/')[-1]}", text_color="white")

        self.path_config_file = (file_path)


    def _handle_run(self):      
        self.result_box.delete("1.0", "end")

        if not hasattr(self, 'path_selected_data') or not hasattr(self, 'path_config_file'):
            messagebox.showwarning("Missing Files", "Please select both Data and Config files first!")
        self.result_box.insert("end", ">>> Starting validation...\n")

        try:
            with open(self.path_config_file, 'r', encoding='utf-8') as f:
                config=json.load(f)

            self.validator._generate_model(config)

            with open(self.path_selected_data, 'r', encoding='utf-8') as f:
                data = json.load(f)

            report_finals = self.validator.verify(data)

            for res in report_finals:
                status_symbol = "✅" if res['status'] == 'OK' else "❌"
                line_msg = f"{status_symbol} Line {res['line']}: {res['status'].upper()}\n"
                self.result_box.insert("end", line_msg)
                
                if res['status'] == 'error':
                    for detail in res['details']:
                        self.result_box.insert("end", f"   |-- {detail}\n")
            
            saved_path = self.validator.json_export(report_finals)
            self.result_box.insert("end", f"\n>>> SUCCESS! Report saved to: {saved_path}\n")
            self.status_label.configure(text="Scan complete", text_color="#2ecc71")

        except ValueError as e:
            self.result_box.insert("end", f"\n❌ CONFIG ERROR: {str(e)}\n", "error_tag")
            messagebox.showerror("Config Error", f"Invalid parameters in settings: {e}")
            
        except json.JSONDecodeError:
            self.result_box.insert("end", f"\n❌ JSON ERROR: One of the files has invalid JSON format!\n")
            messagebox.showerror("File Error", "Failed to parse JSON. Check file formatting.")
            
        except Exception as e:
            self.result_box.insert("end", f"\n❌ SYSTEM CRITICAL ERROR: {str(e)}\n")
            print(f"Full traceback: {e}")
            messagebox.showerror("Critical Error", f"Something went wrong: {e}")
        

if __name__ == "__main__":
    app = DataValidatorGUI()
    app.mainloop()