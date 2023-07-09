from owlready2 import *
from coupled_modelling import sync_entity


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

        class CoupledSystem(Thing):
            label = ["Coupled system"]
            #comment = []

        class Solver(Thing):
            label = ["Solver"]
            #comment = []

    # Object properties        
        class hasVariable(ObjectProperty):
            label = ["has variable"]
            domain = [Model, Solver]  
            range = [Variable]

        class hasInput(hasVariable):
            label = ["has input"]
            domain = [Model]  
            range = [Variable]
        
        class hasOutput(hasVariable):
            label = ["has output"]
            domain = [Model]
            range = [Variable]

        class hasCoupledSystem(ObjectProperty):
            label = ["has coupled system"]
            domain = [Model]
            range = [CoupledSystem]

        class hasSolver(ObjectProperty):
            label = ["has solver"]
            domain = [Model]
            range = [Solver]

    # Annotation properties
        class wikidata(AnnotationProperty):
            pass

        class dbpedia(AnnotationProperty):
            pass

    for cl in onto.classes():
        sync_entity(cl)
    
    onto.save('onto.owl')


if __name__ == "__main__":
    main()
