import os
import json
from coupled_modelling import *


input_path = os.path.join(
    os.path.dirname(os.path.abspath('')),
    'examples/mixed_fid_models/',
    'ProjectParametersCoSimFSI.json')

with open(input_path) as f:
    data = json.load(f)

from coupled_modelling import KnowledgeBase

kb = KnowledgeBase('http://127.0.0.1:5000/api/v1.0/')

mixed_fid_models = kb.import_kratos('mixed_fid_models', data)

# mixed_fid_models = kb.import_coupled_kratos('mixed_fid_models', data)

weak_coupled_model = kb.create_coupled('3Field_coupling')

problem_data_mixed = kb.get_instance(mixed_fid_models.get_properties()["problem_data"])

#problem data
problem_data_new = problem_data_mixed.make_copy(weak_coupled_model, {'parallel_type': 'MPI'})

#solver_settings
solver_settings_old = kb.get_instance(mixed_fid_models.get_properties()["solver_settings"])
solver_settings_new = kb.create_instance("solver_settings", weak_coupled_model, {'echo_level': 3, 'type': 'coupled_solvers.gauss_seidel_weak'})

# new coupling sequence
coupling_sequence_new_0 = kb.create_instance("coupling_sequence", solver_settings_new, {"name": "CFD"})

coupling_sequence_old_1 = kb.get_instance(solver_settings_old.get_properties()['coupling_sequence'][1])
coupling_sequence_new_1 = coupling_sequence_old_1.make_copy(solver_settings_new, recursive=True)

# data transfer operators
dto_old_0 = kb.get_instance(solver_settings_old.get_properties()['data_transfer_operators'])
dto_new_0 = dto_old_0.make_copy(solver_settings_new, recursive=False)

mapper_settings = kb.create_instance("mapper_settings", dto_new_0, {"echo_level": 3, "mapper_type": "barycentric"})


# solvers
solver_old_0 = kb.get_instance(solver_settings_old.get_properties()['solvers'][0])
solver_new_0 = solver_old_0.make_copy(solver_settings_new, recursive=True)
# raise RuntimeError("Check why the following line does not work")

solver_old_1 = kb.get_instance(solver_settings_old.get_properties()['solvers'][1])
solver_new_1 = solver_old_1.make_copy(solver_settings_new, recursive=True)

export = weak_coupled_model.export_kratos()

export_path = os.path.join(
    os.path.abspath(''),
    'export_fsi_weak.json')

with open(export_path, 'w') as file:
    json.dump(export, file, indent=2)

