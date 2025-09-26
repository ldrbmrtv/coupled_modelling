import os
import json
from coupled_modelling import *


input_path = os.path.join(
    os.path.dirname(os.path.abspath('')),
    'examples/mixed_fid_models/',
    'ProjectParametersCoSimFSI.json')

with open(input_path) as f:
    data = json.load(f)

data

from coupled_modelling import KnowledgeBase

kb = KnowledgeBase('http://127.0.0.1:5000/api/v1.0/')

kb

mixed_fid_models = kb.import_kratos('mixed_fid_models', data)

new_coupled_model = kb.create_coupled('3Field_coupling')

mixed_fid_models = kb.import_kratos('mixed_fid_models', data)

data = kb.create_instance(
    "problem_data",
    new_coupled_model,
    {
        'start_time': 0.0,
        'end_time': 1.0,
        'echo_level': 0,
        'print_colors': True,
        'parallel_type': 'OpenMP'
    }
)

export = new_coupled_model.export_kratos()
print(export)