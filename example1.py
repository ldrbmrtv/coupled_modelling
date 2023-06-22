from janus import *
import json


def calc_lift(Slope, Span):
    return Slope + Span

def calc_angle(Chord, Lift):
    return Chord + Lift


def main():
    onto = load_onto('onto.owl')

    # Creating variables
    with open('variables.json', 'r') as f:
        variables = json.load(f)
        create_variables(onto, variables)

    # Creating coupled system
    with open('coupled.json', 'r') as f:
        coupled_models = json.load(f)
        create_coupled(onto, 'CoupledSystem', coupled_models)

    # Sync with Wikidata/DBpedia
    sync_onto(onto)

    # Describing models
    with open('models.json', 'r') as f:
        models = json.load(f)
        describe_models(onto, 'CoupledSystem', models)

    # Instanciating coupled system
    coupled_inst = initialize_coupled(onto, 'CoupledSystem')

    # Creating variable values
    with open('values.json', 'r') as f:
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
