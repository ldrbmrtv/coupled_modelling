import os
import json
from coupled_modeling import KnowledgeBase

input_path = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    'mixed_fid_models/',
    'ProjectParametersCoSimFSI.json')

with open(input_path) as f:
    data = json.load(f)


kb = KnowledgeBase('http://127.0.0.1:5000/api/v1.0/')

kb.import_coupled_kratos('mixed_fid_models', data)

coupled_system = kb.create_coupled('Onera_FSI')

problem_data = kb.copy_instance(
    'instance_2',
    coupled_system,
    {'echo_level': 2})

solver_settings = kb.copy_instance(
    'instance_3',
    coupled_system,
    {'echo_level': 4})

convergence_accelerators = kb.create_instance(
    'convergence_accelerators',
    solver_settings,
    {'data_name': 'displacements', 'solver': 'CFD', 'type': 'aitken'})

convergence_criteria = kb.copy_instance('instance_7', solver_settings, {
    'data_name': 'displacements',
    'solver': 'CFD',
    'type': 'relative_norm_initial_residual'})

coupling_sequence = kb.create_instance('coupling_sequence', solver_settings, {
    'name': 'CFD'})

coupling_sequence = kb.create_instance('coupling_sequence', solver_settings, {
    'name': 'SM'})

input_data_list = kb.copy_instance('instance_10', coupling_sequence, {
    'data_transfer_operator': 'mapping_operation',
    'from_solver': 'CFD',
    'data_transfer_operator_options': 'use_transpose'})

output_data_list = kb.create_instance('output_data_list', coupling_sequence, {
    'data': 'displacements',
    'data_transfer_operator': 'mapping_operation',
    'to_solver': 'CFD',
    'to_solver_data': 'displacements'})

mapping_operation = kb.create_instance('data_transfer_operators', solver_settings, {
    'label': 'mapping_operation',
    'type': 'kratos_mapping'})

mapper_settings = kb.create_instance('mapper_settings', mapping_operation, {
    'mapper_type': 'nearest_neighbor',
    'use_initial_configuration': True})

CFD = kb.copy_instance('instance_12', solver_settings, {
    'label': 'CFD'})

displacements = kb.create_instance('data', CFD, {
    'label': 'displacements',
    'dimensions': 3,
    'model_part_name': 'WING',
    'variable_name': 'MESH_DISPLACEMENT'})

lift_force = kb.create_instance('data', CFD, {
    'label': 'lift_force',
    'dimensions': 3,
    'model_part_name': 'WING',
    'variable_name': 'REACTION'})

io_settings = kb.copy_instance('instance_14', CFD, {
    'connect_to': 'run_SU2'})

solver_wrapper_settings = kb.copy_instance('instance_13', CFD, {
    'export_data': 'displacements',
    'import_meshes': 'WING'})

SM = kb.create_instance('solvers', solver_settings, {
    'label': 'SM',
    'type': 'solver_wrappers.kratos.structural_mechanics_wrapper'})

displacements = kb.copy_instance(displacements, SM, {
    'model_part_name': 'Structure.interface',
    'variable_name': 'DISPLACEMENT'})

lift_force = kb.copy_instance(lift_force, SM, {
    'model_part_name': 'Structure.interface',
    'variable_name': 'POINT_LOAD'})

solver_wrapper_settings = kb.create_instance('solver_wrapper_settings', SM, {
    'input_file': 'ProjectParametersSM'})

kb.infer_coupled_structure(coupled_system)
kb.save()

export = kb.export_coupled_kratos(coupled_system)

with open('export_onera_fsi.json', 'w') as file:
    json.dump(export, file, indent=2)
