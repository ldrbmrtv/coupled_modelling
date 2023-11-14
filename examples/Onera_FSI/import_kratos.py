from coupled_modelling import *
import json


def main():
    input_path = 'ProjectParametersCoSimFSI.json'    
    onto = get_onto('Onera_FSI')
    
    with open(input_path) as f:
        data = json.load(f)

    import_coupled_kratos(onto, data, 'Onera_FSI')
    save_onto(onto, 'Onera_FSI.owl')
    
    
if __name__ == "__main__":
    main()
