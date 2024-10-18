from coupled_modelling import *
import json


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

print('Creating a new solver instance')
test_solver = add_statement(onto, test_solver_settings, 'has_solvers')
print('\n')

print('Adding a label to the created solver instance')
add_statement(onto, test_solver, 'label', 'test_solver')
print('\n')

save_onto(onto)

print('Checking that the new coupled system appeared amongs instences of coupled systems')
print(get_instance_options(onto, 'coupled_system'))
print('\n')

print('Checking properies of the new coupled system')
print(get_instance_properties(onto, test_coupled.name))
print('\n')

print('Checking properties of the connected instance')
print(get_instance_properties(onto, test_solver_settings.name))
print('\n')

print('Getting instance properties recursively')
export = get_instance_properties_recursively(onto, test_coupled.name)
print(export)
with open('export.json', 'w') as file:
    json.dump(export, file, indent=2)
print('\n')

print('Getting instance properties recursively in Kratos format')
export = export_coupled_kratos(onto, 'coupled_system1')
print(export)
with open('export_kratos.json', 'w') as file:
    json.dump(export, file, indent=2)
