from coupled_modelling import *
import json


def main():
    input_path = 'ProjectParametersCoSimFSI.json'    
    with open(input_path) as f:
        data = json.load(f)

    import_coupled_kratos(data, 'mixed_fid_models')
    save_onto()
    
    
if __name__ == "__main__":
    main()
