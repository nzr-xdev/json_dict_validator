# 📃 Dynamic JSON Validator

![GitHub Python version](https://img.shields.io/badge/python-3.10+-blue.svg)
![Pydantic](https://img.shields.io/badge/library-pydantic-orange.svg)
![CustomTkinter](https://img.shields.io/badge/UI-CustomTkinter-blueviolet.svg)

A powerful tool designed to validate large JSON datasets using dynamic pydantic models.

---

### 🧰 Core Features

* **Dynamic Model Generation**: Creates validation rules on the fly based on user configuration.
* **Parameter Cleaning**: Automatically filters invalid parameters and injects default presets for strings and numbers.
* **Advanced Logic Support**:
    * **Regex Patterns**: Validate IDs, codes, or custom string formats.
    * **Numerical Ranges**: Checks for `greater than`, `less than`, or `equal`.
    * **Email Validation**: Built-in verification for emails.
* **Detailed Reporting**: Generates an audit of your data, highlighting exact error locations and reasons.

*some features will arive later*

<!--### 🎮 GUI Preview

| Config Interface | Validation Report |
| :---: | :---: |
| ![config_img](images/config.png) | ![report_img](images/report.png) | -->

### 🚀 Stack & Tools
* **Language**: **Python** — core engine.
* **Logic**: **Pydantic V2** — high-speed data validation and type enforcement.
* **UI/UX**: **CustomTkinter** — modern, dark-themed desktop interface. *(in process)*

### 🔩 How to run:
1. **Clone the repository**:
   ```bash
   git clone https://github.com/nzr-xdev/json_dict_validator.git
2. **Setup environment & requirements:**:
   ```bash
   pip install -r requirements.txt
3. **Run Application:**:
   (just for test)
   ```bash
   python "core.py" 
