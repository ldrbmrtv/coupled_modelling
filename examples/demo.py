from coupled_modelling import *
import json


onto = load_onto()

print('Creating a new empty coupled system')
test_coupled = create_coupled(onto, 'test')
print(test_coupled.name)
print('\n')

print('Checking that the new coupled system appeared amongs instences of coupled systems')
print(get_instance_options(onto, 'coupled_system'))
print('\n')

print('Copying an existing connected instance recursively')
test_solver_settings = copy_instance_recursively(onto, 'solver_settings1')
print(test_solver_settings.name)
print('\n')

print('Adding a property to the copied instance')
add_statement(onto, test_solver_settings, 'has_num_coupling_iterations', 30)
delete_statement(onto, test_solver_settings, 'has_num_coupling_iterations', 20)
print(get_instance_properties(onto, test_solver_settings.name))
print('\n')

print('Connecting copied instances to the created coupled system')
add_statement(onto, test_coupled, 'has_solver_settings', test_solver_settings)
print(get_instance_properties(onto, test_coupled.name))
print('\n')

save_onto(onto)

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
