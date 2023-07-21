from coupled_modelling import *
import json


def main():
    input_path = 'input'    
    onto = load_onto()
    
    # Creating variables
    with open(os.path.join(input_path, 'variables.json'), 'r') as f:
        variables = json.load(f)
        create_variables(onto, variables, False)

    # Creating solvers
    with open(os.path.join(input_path, 'solvers.json'), 'r') as f:
        solvers = json.load(f)
        create_solvers(onto, solvers, False)

    # Creating models
    with open(os.path.join(input_path, 'models.json'), 'r') as f:
        models = json.load(f)
        coupled_system = create_models(onto, models, 'CoupledSystem1', False)

    # Saving
    save_onto(onto, 'multidisciplinary_model.owl')

    with open('kratos.json', 'w') as f:
        result = export_coupled_for_kratos(onto, coupled_system)
        json.dump(result, f, indent = 2)

    
if __name__ == "__main__":
    main()
