from main import *
from owlready2 import *
import os
import json


input_path_1 = os.path.join(
    os.path.dirname(os.path.abspath('')),
    'examples',
    'mixed_fid_models',
    'ProjectParametersCoSimFSI.json')

input_path_2 = os.path.join(
    os.path.dirname(os.path.abspath('')),
    'examples',
    'Onera_FSI',
    'ProjectParametersCoSimFSI.json')

inputs = {
    'mixed_fid_models': input_path_1,
    'Onera_FSI': input_path_2
}

for label, path in inputs.items():
    with open(path) as f:
        data = json.load(f)
    import_coupled_kratos(data, label)
    
save_onto()

export_path = os.path.join(
    os.path.dirname(os.path.abspath('')),
    'examples',
    'test.owl')

onto.save(export_path)