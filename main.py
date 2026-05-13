import customtkinter as ctk
from tkinter import filedialog, messagebox
from core import DataValidator
from time import perf_counter
import json
import os

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class DataValidatorGUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("JSON Data Validator")
        self.geometry("1100x650")
        self.validator = DataValidator()
        self.path_data = None
        self.path_config = None
        self.ignore_missing_var = ctk.BooleanVar(value=False)
        try: self.iconbitmap("assets/icon.ico")
        except Exception as e: print(f'Failed to load the icon \n{e}')

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)

        self.result_box = ctk.CTkTextbox(self, font=("Consolas", 13), fg_color="#121212")
        self.result_box.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        self.result_box.tag_config("error_line", background="#4e1a1a")
        self.result_box.tag_config("ok_line", background="#2d5f2d")
        self.result_box.tag_config("error_detail", foreground="#e4503f")
        self.result_box.tag_config("missing_line", background="#96962f", foreground="white")
        
        self.bottom_panel = ctk.CTkFrame(self, height=50, corner_radius=10)
        self.bottom_panel.grid(row=1, column=0, sticky="ew", padx=5, pady=(0,10))

        self.run_btn = ctk.CTkButton(self.bottom_panel, text="RUN VALIDATION", fg_color="#2ecc71", 
                                    hover_color="#27ae60", font=ctk.CTkFont(weight="bold"), 
                                    width=140, height=32, command=self._handle_run)
        self.run_btn.pack(side="left", padx=(20, 10), pady=10)

        self.load_data_btn = ctk.CTkButton(self.bottom_panel, text="📁 Data", width=80, height=32, command=self._load_data)
        self.load_data_btn.pack(side="left", padx=5)

        self.load_conf_btn = ctk.CTkButton(self.bottom_panel, text="⚙️ Config", width=80, height=32, command=self._load_config)
        self.load_conf_btn.pack(side="left", padx=5)

        self.clear_btn = ctk.CTkButton(self.bottom_panel, text="🧹 Clear", width=80, height=32, fg_color="#e74c3c", command=self._clear_all)
        self.clear_btn.pack(side="left", padx=5)

        self.ignore_check = ctk.CTkCheckBox(self.bottom_panel, text="Ignore Missing", 
                                           variable=self.ignore_missing_var, font=("Inter", 12))
        self.ignore_check.pack(side="left", padx=15)

        self.data_label = ctk.CTkLabel(self.bottom_panel, text="Data: None", font=("Inter", 12, "bold"), text_color="#3498db")
        self.data_label.pack(side="left", padx=15)

        self.conf_label = ctk.CTkLabel(self.bottom_panel, text="Config: None", font=("Inter", 12, "bold"), text_color="#f1c40f")
        self.conf_label.pack(side="left", padx=15)

        self.stats_label = ctk.CTkLabel(self.bottom_panel, text="✔: 0 | ❌: 0 | 0.0%", 
                                        font=("Consolas", 13, "bold"), text_color="#ffffff")
        self.stats_label.pack(side="right", padx=20)

    def _load_data(self):
        path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if path:
            self.path_data = path
            self.data_label.configure(text=f"Data: {os.path.basename(path)}")
            with open(path, 'r', encoding='utf-8') as f:
                self.result_box.configure(state="normal")
                self.result_box.delete("1.0", "end")
                self.result_box.insert("1.0", f.read())

    def _clear_all(self):
        self.path_data, self.path_config = None, None
        self.data_label.configure(text="Data: None")
        self.conf_label.configure(text="Config: None")
        self.result_box.configure(state="normal")
        self.result_box.delete("1.0", "end")
        self.stats_label.configure(text="✔: 0 | ❌: 0 | 0.0%")

    def _load_config(self):
        path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if path:
            self.path_config = path
            self.conf_label.configure(text=f"Config: {os.path.basename(path)}", text_color="#d4af18")

    def _handle_run(self):
            if not self.path_data or not self.path_config:
                messagebox.showwarning("Warn", "Choose the data/config file!")
                return
            
            try:
                with open(self.path_data, 'r', encoding='utf-8') as f:
                    raw_input = f.read().strip()
            except Exception:
                raw_input = self.result_box.get("1.0", "end-1c").strip()

            if not raw_input: 
                messagebox.showwarning("Warn", "Here is no data")
                return

            self.result_box.configure(state="normal")
            self.result_box.delete("1.0", "end")

            t_start = perf_counter()

            try:
                parsed_data = json.loads(raw_input)
                formatted_json = json.dumps(parsed_data, indent=4, ensure_ascii=False)
                lines = formatted_json.split('\n')
                ignore_missing = self.ignore_missing_var.get()
                
                with open(self.path_config, 'r', encoding='utf-8') as f:
                    self.validator._generate_model(json.load(f))
                
                report = self.validator.verify(parsed_data)
                self.validator.json_export(report)
                
                c_ok, c_err = 0, 0
                current_case_idx = -1
                used_errors = []

                for i, line_content in enumerate(lines):
                    line_num = i + 1
                    clean_line = line_content.strip()
                    
                    if "{" in clean_line:
                        current_case_idx += 1
                        used_errors = []
                    
                    line_errors = []
                    is_missing_type = False
                    
                    if 0 <= current_case_idx < len(report):
                        case_res = report[current_case_idx]
                        
                        if case_res['status'] == 'error':
                            for detail in case_res.get('details', []):
                                field = detail.split(':')[0]
                                if f'"{field}"' in line_content:
                                    line_errors.append(detail)
                                    used_errors.append(detail)

                    prefix = f"{line_num} "
                    if line_errors:
                        self.result_box.insert("end", f"{prefix}▶ {line_content}\n", "error_line")
                        for d in list(set(line_errors)):
                            self.result_box.insert("end", f"   ! {d}\n", "error_detail")
                        c_err += 1
                    elif ":" in clean_line and not any(x in clean_line for x in ["{", "["]):
                        self.result_box.insert("end", f"{prefix}✓ {line_content}\n", "ok_line")
                        c_ok += 1
                    else:
                        self.result_box.insert("end", f"{prefix}  {line_content}\n")

                    if "}" in clean_line and 0 <= current_case_idx < len(report):
                        case_res = report[current_case_idx]
                        if case_res['status'] == 'error':
                            missing_errors = [d for d in case_res['details'] if d not in used_errors]
                            
                            if missing_errors and not ignore_missing:
                                for m_err in missing_errors:
                                    self.result_box.insert("end", f"      ⚠ MISSING FIELD: {m_err}\n", "missing_line")
                                    c_err += 1

                self._update_stats(c_ok, c_err)
                self.result_box.insert("end", f"Time elapsed: {perf_counter() - t_start:.2f} sec", "ok_line")

            except json.JSONDecodeError as je:
                self.result_box.insert("end", f"❌ JSON file has an error:\n{str(je)}", "error_line")
                messagebox.showerror("Format Error", f"Failed to parse JSON file. Check terminal output", "error_line")
                self.result_box.insert("end", f"Time elapsed: {perf_counter() - t_start:.2f} sec", "ok_line")
            except Exception as e:
                self.result_box.insert("end", f"❌ SYSTEM ERROR: {e}", "error_line")
                self.result_box.insert("end", f"Time elapsed: {perf_counter() - t_start:.2f} sec", "ok_line")
            
            self.result_box.configure(state="disabled")

    def _update_stats(self, correct, incorrect):
        total = correct + incorrect
        perc = round((correct / total * 100), 1) if total > 0 else 0
        self.stats_label.configure(
            text=f"✔: {correct} | ❌: {incorrect} | {perc}%",
            text_color="#2ecc71" if perc == 100 else "#e74c3c"
        )

if __name__ == "__main__":
    app = DataValidatorGUI()
    app.mainloop()