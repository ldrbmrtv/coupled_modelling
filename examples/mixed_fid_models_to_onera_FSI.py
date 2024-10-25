from coupled_modelling import *


coupled_system = create_coupled('Onera_FSI')

problem_data = copy_instance('problem_data1', coupled_system)
replace_value(problem_data, 'echo_level', 2)

solver_settings = add_value(coupled_system, 'solver_settings')

convergence_accelerators = add_value(solver_settings, 'convergence_accelerators')
add_value(convergence_accelerators, 'data_name', 'displacements')
add_value(convergence_accelerators, 'solver', 'CFD')
add_value(convergence_accelerators, 'type', 'aitken')

convergence_criteria = copy_instance('convergence_criteria1', solver_settings)
replace_value(convergence_criteria, 'data_name', 'displacements')
replace_value(convergence_criteria, 'solver', 'CFD')
replace_value(convergence_criteria, 'type', 'relative_norm_initial_residual')

coupling_sequence = add_value(solver_settings, 'coupling_sequence')
add_value(coupling_sequence, 'name', 'CFD')

coupling_sequence = add_value(solver_settings, 'coupling_sequence')

input_data_list = copy_instance('input_data_list1', coupling_sequence)
replace_value(input_data_list, 'data_transfer_operator', 'mapping_operation')
add_value(input_data_list, 'data_transfer_operator_options', 'use_transpose')
replace_value(input_data_list, 'solver', 'CFD')

add_value(coupling_sequence, 'name', 'SM')

output_data_list = add_value(coupling_sequence, 'output_data_list')
add_value(output_data_list, 'data', 'displacements')
add_value(output_data_list, 'data_transfer_operator', 'mapping_operation')
add_value(output_data_list, 'to_solver', 'CFD')
add_value(output_data_list, 'to_solver_data', 'displacements')

save_onto()









