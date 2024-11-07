from coupled_modelling import *
import json


coupled_system = create_coupled('Onera_FSI')

problem_data = copy_instance('instance_2', coupled_system, {
    'echo_level': 2})

solver_settings = copy_instance('instance_3', coupled_system, {
    'echo_level': 4})

convergence_accelerators = create_instance('convergence_accelerators', solver_settings, {
    'data_name': 'displacements',
    'solver': 'CFD',
    'type': 'aitken'})

convergence_criteria = copy_instance('instance_7', solver_settings, {
    'data_name': 'displacements',
    'solver': 'CFD',
    'type': 'relative_norm_initial_residual'})

coupling_sequence = create_instance('coupling_sequence', solver_settings, {
    'name': 'CFD'})

coupling_sequence = create_instance('coupling_sequence', solver_settings, {
    'name': 'SM'})

input_data_list = copy_instance('instance_10', coupling_sequence, {
    'data_transfer_operator': 'mapping_operation',
    'from_solver': 'CFD',
    'data_transfer_operator_options': 'use_transpose'})

output_data_list = create_instance('output_data_list', coupling_sequence, {
    'data': 'displacements',
    'data_transfer_operator': 'mapping_operation',
    'to_solver': 'CFD',
    'to_solver_data': 'displacements'})

mapping_operation = create_instance('data_transfer_operators', solver_settings, {
    'label': 'mapping_operation',
    'type': 'kratos_mapping'})

mapper_settings = create_instance('mapper_settings', mapping_operation, {
    'mapper_type': 'nearest_neighbor',
    'use_initial_configuration': True})
                                
CFD = copy_instance('instance_12', solver_settings, {'label': 'CFD'})

displacements = create_instance('data', CFD, {
    'label': 'displacements',
    'dimensions': 3,
    'model_part_name': 'WING',
    'variable_name': 'MESH_DISPLACEMENT'})

lift_force = create_instance('data', CFD, {
    'label': 'lift_force',
    'dimensions': 3,
    'model_part_name': 'WING',
    'variable_name': 'REACTION'})
        
io_settings = copy_instance('instance_14', CFD, {'connect_to': 'run_SU2'})

solver_wrapper_settings = copy_instance('instance_13', CFD, {
    'export_data': 'displacements',
    'import_meshes': 'WING'})

SM = create_instance('solvers', solver_settings, {
    'label': 'SM',
    'type': 'solver_wrappers.kratos.structural_mechanics_wrapper'})

displacements = copy_instance(displacements, SM, {
    'model_part_name': 'Structure.interface',
    'variable_name': 'DISPLACEMENT'})

lift_force = copy_instance(lift_force, SM, {
    'model_part_name': 'Structure.interface',
    'variable_name': 'POINT_LOAD'})

solver_wrapper_settings = create_instance('solver_wrapper_settings', SM, {
    'input_file': 'ProjectParametersSM'})

infer_coupled_system_structure(coupled_system)

save_onto()

export = export_coupled_kratos(coupled_system)
with open('export_onera_fsi.json', 'w') as file:
    json.dump(export, file, indent=2)










