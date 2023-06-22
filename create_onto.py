from owlready2 import *


def main():
    onto_path.append('')
    onto = get_ontology("http://b4-1/ontologies/2023/1/onto")

    with onto:

    # Classes
        class Model(Thing):
            label = ["Model"]
            comment = ["A mathematical model is a function that maps an input to an output."]

        class Variable(Thing):
            label = ["Variable"]
            #comment = []

    # Object properties        
        class hasVariable(ObjectProperty):
            label = ["has variable"]
            domain = [Model]  
            range = [Variable]

        class hasInput(hasVariable):
            label = ["has input"]
            domain = [Model]  
            range = [Variable]
        
        class hasOutput(hasVariable):
            label = ["has output"]
            domain = [Model]
            range = [Variable]

    onto.save('onto.owl')


if __name__ == "__main__":
    main()
