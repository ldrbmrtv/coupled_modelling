from coupled_modelling import *


coupled_system = create_coupled('Onera_FSI')

problem_data = copy_instance('problem_data1', coupled_system, {'echo_level': 2})

solver_settings = create_instance(coupled_system, 'solver_settings')

convergence_accelerators = create_instance(
    solver_settings, 'convergence_accelerators',
    {
        'data_name': 'displacements',
        'solver': 'CFD',
        'type': 'aitken'
    }
)

convergence_criteria = copy_instance(
    'convergence_criteria1', solver_settings,
    {
        'data_name': 'displacements',
        'solver': 'CFD',
        'type': 'relative_norm_initial_residual'
    }
)

coupling_sequence = create_instance(
    solver_settings, 'coupling_sequence', {'name': 'CFD'}
)

coupling_sequence = create_instance(
    solver_settings, 'coupling_sequence',
    {
        'name': 'SM'
    }
)

input_data_list = copy_instance(
    'input_data_list1', coupling_sequence,
    {
        'data_transfer_operator': 'mapping_operation',
        'solver': 'CFD'
    }
)
add_value(input_data_list, 'data_transfer_operator_options', 'use_transpose')

output_data_list = create_instance(
    coupling_sequence, 'output_data_list',
    {
        'data': 'displacements',
        'data_transfer_operator': 'mapping_operation',
        'to_solver': 'CFD',
        'to_solver_data': 'displacements'
    }
)

save_onto()









