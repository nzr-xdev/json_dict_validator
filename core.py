from pydantic import EmailStr, Field, create_model, ValidationError
import json
from datetime import datetime
from pathlib import Path

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

    def __init__(self):
        self.model = None
        self.last_stat = None

    def json_export(self, report, folder_path="reports"):

        dir = Path(folder_path)
        dir.mkdir(parents=True, exist_ok=True)
        time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        file_name = f"report_{time}.json"
        path = dir / file_name

        with open(path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=4)
        return str(path)

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
    
    def _generate_model(self, user_config: dict):

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

    def verify(self, data_list: list):    

        if self.model is None:
            print("CRITICAL: Model is not generated")
            return []

        report = []

        for index, item in enumerate(data_list):
            try:

                self.model.model_validate(item)
                report.append({
                    'set': index+1, 
                    "status": 'OK'})
                
            except ValidationError as e:

                errors = []

                for err in e.errors():
                    fd = err['loc'][0]
                    msg = err['msg']
                    errors.append(f"{fd}: {msg}")
                
                report.append({
                    'set': index+1, 
                    "status": 'error',
                    "details": errors
                    })
            except Exception as e:
                report.append({
                    "set": index + 1,
                    "status": "error",
                    "details": [f"System error: {str(e)}"]
                })

        return report