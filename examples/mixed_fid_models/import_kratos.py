from coupled_modelling import *
import json


def main():
    input_path = 'ProjectParametersCoSimFSI.json'    
    onto = get_onto('mixed_fid_models')
    
    with open(input_path) as f:
        data = json.load(f)

    import_coupled_kratos(onto, data, 'mixed_fid_models')
    save_onto(onto, 'mixed_fid_models.owl')
    
    
if __name__ == "__main__":
    main()
