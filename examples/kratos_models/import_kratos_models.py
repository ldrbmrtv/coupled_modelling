from coupled_modelling import *
import json


def main():
    onto = get_onto('kratos_models')

    input_path = 'low_fid_models.json'    
    with open(input_path) as f:
        data = json.load(f)
    import_coupled_kratos(onto, data, 'lfm', 'low_fid_models')

    input_path = 'Onera_FSI.json'    
    with open(input_path) as f:
        data = json.load(f)
    import_coupled_kratos(onto, data, 'ofsi', 'Onera_FSI')
    
    save_onto(onto, 'kratos_models.owl')
    
    
if __name__ == "__main__":
    main()
