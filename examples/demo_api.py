import os
import json
import requests


host = 'http://127.0.0.1:5000/api/v1.0/'

input_path = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    'mixed_fid_models/',
    'ProjectParametersCoSimFSI.json')

with open(input_path) as f:
    data = json.load(f)
        
params = {'data': data, 'label': 'mixed_fid_models'}
res = requests.post(f'{host}import_coupled_kratos', json=params)

params = {'label': 'Onera_FSI'}
res = requests.post(f'{host}create_coupled', json=params)
coupled_system = res.json()

params = {
    'instance': 'instance_2',
    'parent': coupled_system,
    'data': {'echo_level': 2}}
res = requests.post(f'{host}copy_instance', json=params)
problem_data = res.json()

params = {
    'instance': 'instance_3',
    'parent': coupled_system,
    'data': {'echo_level': 4}}
res = requests.post(f'{host}copy_instance', json=params)
solver_settings = res.json()

params = {
    'property': 'convergence_accelerators',
    'parent': solver_settings,
    'data': {
        'data_name': 'displacements',
        'solver': 'CFD',
        'type': 'aitken'}}
res = requests.post(f'{host}create_instance', json=params)
convergence_accelerators = res.json()

params = {
    'instance': 'instance_7',
    'parent': solver_settings,
    'data': {
        'data_name': 'displacements',
        'solver': 'CFD',
        'type': 'relative_norm_initial_residual'}}
res = requests.post(f'{host}copy_instance', json=params)
convergence_criteria = res.json()

params = {
    'property': 'coupling_sequence',
    'parent': solver_settings,
    'data': {'name': 'CFD'}}
res = requests.post(f'{host}create_instance', json=params)
coupling_sequence = res.json()

params = {
    'property': 'coupling_sequence',
    'parent': solver_settings,
    'data': {'name': 'SM'}}
res = requests.post(f'{host}create_instance', json=params)
coupling_sequence = res.json()

params = {
    'instance': 'instance_10',
    'parent': coupling_sequence,
    'data': {
        'data_transfer_operator': 'mapping_operation',
        'from_solver': 'CFD',
        'data_transfer_operator_options': 'use_transpose'}}
res = requests.post(f'{host}copy_instance', json=params)
input_data_list = res.json()

params = {
    'property': 'output_data_list',
    'parent': coupling_sequence,
    'data': {
        'data': 'displacements',
        'data_transfer_operator': 'mapping_operation',
        'to_solver': 'CFD',
        'to_solver_data': 'displacements'}}
res = requests.post(f'{host}create_instance', json=params)
output_data_list = res.json()

params = {
    'property': 'data_transfer_operators',
    'parent': solver_settings,
    'data': {
        'label': 'mapping_operation',
        'type': 'kratos_mapping'}}
res = requests.post(f'{host}create_instance', json=params)
mapping_operation = res.json()

params = {
    'property': 'mapper_settings',
    'parent': mapping_operation,
    'data': {
        'mapper_type': 'nearest_neighbor',
        'use_initial_configuration': True}}
res = requests.post(f'{host}create_instance', json=params)
mapper_settings = res.json()

params = {
    'instance': 'instance_12',
    'parent': solver_settings,
    'data': {'label': 'CFD'}}
res = requests.post(f'{host}copy_instance', json=params)
CFD = res.json()

params = {
    'property': 'data',
    'parent': CFD,
    'data': {
        'label': 'displacements',
        'dimensions': 3,
        'model_part_name': 'WING',
        'variable_name': 'MESH_DISPLACEMENT'}}
res = requests.post(f'{host}create_instance', json=params)
displacements = res.json()

params = {
    'property': 'data',
    'parent': CFD,
    'data': {
        'label': 'lift_force',
        'dimensions': 3,
        'model_part_name': 'WING',
        'variable_name': 'REACTION'}}
res = requests.post(f'{host}create_instance', json=params)
lift_force = res.json()

params = {
    'instance': 'instance_14',
    'parent': CFD,
    'data': {'connect_to': 'run_SU2'}}
res = requests.post(f'{host}copy_instance', json=params)
io_settings = res.json()

params = {
    'instance': 'instance_13',
    'parent': CFD,
    'data': {
        'export_data': 'displacements',
        'import_meshes': 'WING'}}
res = requests.post(f'{host}copy_instance', json=params)
solver_wrapper_settings = res.json()

params = {
    'property': 'solvers',
    'parent': solver_settings,
    'data': {
        'label': 'SM',
        'type': 'solver_wrappers.kratos.structural_mechanics_wrapper'}}
res = requests.post(f'{host}create_instance', json=params)
SM = res.json()

params = {
    'instance': displacements,
    'parent': SM,
    'data': {
        'model_part_name': 'Structure.interface',
        'variable_name': 'DISPLACEMENT'}}
res = requests.post(f'{host}copy_instance', json=params)
displacements = res.json()

params = {
    'instance': lift_force,
    'parent': SM,
    'data': {
        'model_part_name': 'Structure.interface',
        'variable_name': 'POINT_LOAD'}}
res = requests.post(f'{host}copy_instance', json=params)
lift_force = res.json()

params = {
    'property': 'solver_wrapper_settings',
    'parent': SM,
    'data': {'input_file': 'ProjectParametersSM'}}
res = requests.post(f'{host}create_instance', json=params)
solver_wrapper_settings = res.json()

params = {'coupled_system': coupled_system}
res = requests.post(f'{host}infer_coupled_structure', json=params)

res = requests.post(f'{host}save_onto')

params = {'coupled_system': coupled_system}
res = requests.post(f'{host}export_coupled_kratos', json=params)
export = res.json()

with open('export_onera_fsi.json', 'w') as file:
    json.dump(export, file, indent=2)
    
