from coupled_modelling import *


onto = load_onto()

print(get_class_options(onto, 'coupled_system'))
print(get_class_properties(onto, 'coupled_system_coupled_system1'))
print(get_instance_options(onto, 'coupled_system'))
print(get_instance_properties(onto, 'coupled_system1'))
print(get_instance_properties(onto, 'solver_settings1'))

test_coupled = create_coupled(onto, 'test')
test_solver_settings = add_statement(onto, test_coupled, 'has_solver_settings')
add_statement(onto, test_solver_settings, 'has_num_coupling_iterations', 30)
print(get_instance_options(onto, 'coupled_system'))
print(get_instance_properties(onto, 'coupled_system3'))
print(get_instance_properties(onto, 'solver_settings3'))

save_onto(onto)
