from coupled_modelling import *


# Function for calculating Lift
def foo(Lift, ElasticSupportPitchAngle):
    return Lift + ElasticSupportPitchAngle


def main():
    
    # Loading onto
    onto = load_onto('multidisciplinary_model.owl')

    # Adding model to coupled system
    coupled_system = onto['CoupledSystem1']
    model_data = {
        'label': 'Airfoil model',
        'input': ['Lift', 'ElasticSupportPitchAngle'],
        'output': ['ElasticSupportPitchAngle']}
    create_model(onto, 'AirfoilModel', model_data, coupled_system)
    
    # Running model incremetally
    coupled_inst = onto['coupledsystem11']
    for i in range(2):
        create_model_run(onto, onto['AirfoilModel'], coupled_inst, foo)

    # Saving
    save_onto(onto, 'multidisciplinary_model_airfoil.owl')


if __name__ == "__main__":
    main()
