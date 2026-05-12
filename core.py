from pydantic import EmailStr, Field, create_model, ValidationError

DEFAULT_PRESETS = {
    str: {'min_length': 1, 'max_length': 100},
    int: {'ge': 0},
    float: {'ge': 0.0},
    EmailStr: {}
}

SUPPORTED_TYPES = {
    'String': str,
    'Integer': int,
    'Number': float,
    'True/False': bool,
    'Email': EmailStr
}

ALLOWED_KEYS = {
            str: ['min_length', 'max_length', 'pattern'],
            int: ['gt', 'ge', 'lt', 'le'],
            float: ['gt', 'ge', 'lt', 'le'],
            bool: [],
            EmailStr: []
                      
                      }

class DataValidator:

    def __init__(self, path: str, settigs_path: str):
        self.path_file = path
        self.settings_path_file = settigs_path
        self.model = None

    def _apply_logic(self, user_params: dict, type_key: type):
        
        final_params = {}

        allowed = ALLOWED_KEYS.get(type_key, [])

        for key in allowed:
            val = user_params.get(key)

            if val == 0 or val is None:
                final_params[key] = DEFAULT_PRESETS[type_key].get(key)
            else: final_params[key] = val

        if type_key == str:
            if final_params.get('max_length') < final_params.get('min_length'):
                raise ValueError("Max length less than minimal!")
        if type_key in [int, float]:
            min_val = final_params.get('ge') if final_params.get('ge') is not None else final_params.get('gt')
            max_val = final_params.get('le') if final_params.get('le') is not None else final_params.get('lt')

            if min_val is not None and max_val is not None:
                if min_val > max_val:
                    raise ValueError(f"Мінімальне значення ({min_val}) не може бути більшим за максимальне ({max_val})!")
        
        return final_params
    
    def _generate_model(self, user_config):

        """ EXAMPLE::
        user_config: {
            "user_login": {"type": "String", "min_length": 5},
            "user_age": {"type": "Integer", "ge": 18}
        }
        """

        fields = {}

        for name, settings in user_config.items():

            cur_settings = settings.copy()

            type = SUPPORTED_TYPES[cur_settings.pop('type')]
            final_params = self._apply_logic(cur_settings, type)

            fields[name] = (type, Field(**final_params))

        self.model = create_model("DynamicValidatorModel", **fields)

    def verify(self, data_list):    

        if self.model is None:
            print("CRITICAL: Model is not generated")
            return []

        report = []

        for index, item in enumerate(data_list):
            try:

                self.model.model_validate(item)
                report.append({
                    'line': index+1, 
                    "status": 'OK'})
                
            except ValidationError as e:

                errors = []

                for err in e.errors():
                    fd = err['loc'][0]
                    msg = err['msg']
                    errors.append(f"{fd}: {msg}")
                
                report.append({
                    'line': index+1, 
                    "status": 'error',
                    "details": errors
                    })
            except Exception as e:
                report.append({
                    "line": index + 1,
                    "status": "error",
                    "details": [f"System error: {str(e)}"]
                })

        return report


if __name__ == "__main__":
    # --- Initialization ---
    # Creating an instance of DataValidator with dummy paths for testing logic
    validator = DataValidator(path="source.json", settigs_path="config.json")

    # --- Scenario 1: Enterprise User & System Configuration ---
    # Testing multiple constraints: 
    # 1. String length (including default substitution)
    # 2. Integer ranges (age/access levels)
    # 3. Float precision (financial balances)
    # 4. Regex patterns (IDs/Codes)
    # 5. Native Pydantic types (EmailStr)
    
    enterprise_config = {
        "employee_id": {"type": "String", "pattern": r"^[A-Z]{2}-\d{4}$"}, # Format: DE-1234
        "full_name": {"type": "String", "min_length": 0}, # Trigger default min_length=1
        "department_code": {"type": "Integer", "ge": 100, "le": 999},
        "hourly_rate": {"type": "Number", "gt": 15.0},
        "is_remote": {"type": "True/False"},
        "corporate_email": {"type": "Email"}
    }

    print(">>> [TEST PHASE 1]: Dynamic Model Assembly")
    try:
        # Note: calling the corrected method name
        validator._generate_model(enterprise_config)
        print("SUCCESS: Validation model built successfully.\n")
    except Exception as e:
        print(f"CRITICAL FAILURE: Model assembly failed. Details: {e}")

    # --- Scenario 2: Comprehensive Multi-Row Dataset ---
    # Covering: [Valid Entries, Logic Violations, Data Integrity Issues]
    enterprise_dataset = [
        # ✅ Entry 01: Perfect Data (Standard Case)
        {
            "employee_id": "US-5566",
            "full_name": "Alexander Pierce",
            "department_code": 500,
            "hourly_rate": 45.50,
            "is_remote": True,
            "corporate_email": "pierce.a@company.com"
        },
        # ❌ Entry 02: Constraint Violations (Logical Errors)
        {
            "employee_id": "invalid-id-123",  # Regex mismatch
            "full_name": "",                  # Default min_length violation (if preset=1)
            "department_code": 50,            # Below ge=100
            "hourly_rate": 10.0,              # Below gt=15.0
            "is_remote": "sometimes",         # Type mismatch (bool expected)
            "corporate_email": "not_an_email" # Email format violation
        },
        # ❌ Entry 03: System Level Failures (Type Incompatibility)
        {
            "employee_id": "UK-8899",
            "full_name": "Sarah Connor",
            "department_code": "Operations",  # String instead of Int
            "hourly_rate": "Negotiable",      # String instead of Float
            "is_remote": False,
            "corporate_email": "s.connor@sky.net"
        },
        # ✅ Entry 04: Boundary Testing (Edge Cases)
        {
            "employee_id": "EU-0000",
            "full_name": "X",                 # Minimal valid string
            "department_code": 100,           # Edge of 'ge'
            "hourly_rate": 15.01,             # Edge of 'gt'
            "is_remote": 0,                   # Pydantic will cast 0 to False (Success)
            "corporate_email": "x@x.io"       # Minimal valid email
        }
    ]

    print(">>> [TEST PHASE 2]: Mass Data Validation")
    validation_results = validator.verify(enterprise_dataset)

    for record in validation_results:
        indicator = "✅" if record['status'] == 'OK' else "❌"
        header = f"Row {record['line']}: {record['status'].upper()}"
        
        print(f"{indicator} {header}")
        
        if record['status'] == 'error':
            for err_detail in record['details']:
                print(f"    |-- Validation Alert: {err_detail}")

    print("\n>>> [ALL TESTS EXECUTED]")