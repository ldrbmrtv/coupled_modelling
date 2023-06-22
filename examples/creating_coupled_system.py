import os
import sys

path = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(path)
sys.path.append(parent)

from coupled_modelling import *
import json


def calc_lift(Slope, Span):
    return Slope + Span

def calc_angle(Chord, Lift):
    return Chord + Lift


def main():
    input_path = 'input'    
    onto = load_onto()

    # Creating variables
    with open(os.path.join(input_path, 'variables.json'), 'r') as f:
        variables = json.load(f)
        create_variables(onto, variables)

    # Creating coupled system
    with open(os.path.join(input_path, 'coupled.json'), 'r') as f:
        coupled_models = json.load(f)
        create_coupled(onto, 'CoupledSystem', coupled_models)

    # Describing models
    with open(os.path.join(input_path, 'models.json'), 'r') as f:
        models = json.load(f)
        describe_models(onto, 'CoupledSystem', models)

    # Instanciating coupled system
    coupled_inst = initialize_coupled(onto, 'CoupledSystem')

    # Creating variable values
    with open(os.path.join(input_path, 'values.json'), 'r') as f:
        values = json.load(f)
        create_values(onto, values, coupled_inst)

    # Running models
    for i in range(1, 3):
        create_model_run(onto, onto['AerodynamicModel'],
                         coupled_inst,
                         calc_lift)
        create_model_run(onto, onto['StructuralModel'],
                         coupled_inst,
                         calc_angle)

    # Saving
    save_onto(onto, 'multidisciplinary_model.owl')

    
if __name__ == "__main__":
    main()
