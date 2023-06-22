from janus import *


# Function for calculating Lift
def foo(Lift, ElasticSupportPitchAngle):
    return Lift + ElasticSupportPitchAngle


def main():
    
    # Loading onto
    onto = load_onto('multidisciplinary_model.owl')

    # Adding model to coupled system
    coupled_system = onto['CoupledSystem']
    model = add_coupled_model(onto, 'AirfoilModel', coupled_system)
    model_data = {
        "input": ["Lift", "ElasticSupportPitchAngle"],
        "output": "ElasticSupportPitchAngle"}
    describe_model(onto, coupled_system, model, model_data)

    # Running model
    coupled_inst = onto['coupledsystem1']
    create_model_run(onto, model, coupled_inst, foo)

    # Saving
    save_onto(onto, 'multidisciplinary_model_airfoil.owl')


if __name__ == "__main__":
    main()
