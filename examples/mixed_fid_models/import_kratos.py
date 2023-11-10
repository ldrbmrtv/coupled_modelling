from coupled_modelling import *
import json


def main():
    input_path = 'ProjectParametersCoSimFSI.json'    
    onto = load_onto()
    
    with open(input_path) as f:
        data = json.load(f)

    import_coupled_kratos(onto, data)
    save_onto(onto, 'ProjectParametersCoSimFSI.owl')
    
    
if __name__ == "__main__":
    main()
