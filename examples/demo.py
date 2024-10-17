from coupled_modelling import *


onto = load_onto()

print('Getting existing types of coupled systems')
print(get_class_options(onto, 'coupled_system'))
print('\n')

print('Getting properties of a type of coupled systems')
print(get_class_properties(onto, 'coupled_system_coupled_system1'))
print('\n')

print('Getting instances of this type of coupled systems')
print(get_instance_options(onto, 'coupled_system'))
print('\n')

print('Getting properties of a coupled system of this type')
print(get_instance_properties(onto, 'coupled_system1'))
print('\n')

print('Getting properties of an instance that is connected to this coupled system')
print(get_instance_properties(onto, 'solver_settings1'))
print('\n')

print('Creating a new empty coupled system')
test_coupled = create_coupled(onto, 'test')
print('\n')

print('Creating a new instance connected to the created coupled system')
test_solver_settings = add_statement(onto, test_coupled, 'has_solver_settings')
print('\n')

print('Adding a property to the created instance')
add_statement(onto, test_solver_settings, 'has_num_coupling_iterations', 30)
print('\n')

print('Checking that the new coupled system appeared amongs instences of coupled systems')
print(get_instance_options(onto, 'coupled_system'))
print('\n')

print('Checking properies of the new coupled system')
print(get_instance_properties(onto, test_coupled.name))
print('\n')

print('Checking properties of the connected instance')
print(get_instance_properties(onto, test_solver_settings.name))
print('\n')

save_onto(onto)
