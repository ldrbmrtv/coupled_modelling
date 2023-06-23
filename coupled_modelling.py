from owlready2 import *
import types
from onto_sync import util_falcon
import os


def get_onto_path():
    return os.path.dirname(os.path.realpath(__file__))


def load_onto(path=None, name='onto.owl'):
    if not path:
        path = get_onto_path()
    onto_path.append(path)
    onto = get_ontology(name).load()

    return onto


def sync_entity(entity):
    if len(entity.label) != 1:
        return
    syncs = util_falcon(entity.label[0])
    if syncs:
        if syncs.get('entities_wiki'):
            entity.wikidata = syncs['entities_wiki']
        if syncs.get('entities_db'):
            entity.wikidata = syncs['entities_db']


def create_variable(onto, name, annos):
    with onto:
        
        # Data Property
        prop = types.new_class(f'has{name}', (DataProperty, FunctionalProperty))
        prop.label = f'has {annos["label"].lower()}'
        prop.domain = [onto.Variable]
        prop.range = [float]

        # Class
        cl = types.new_class(name, (onto.Variable,))
        cl.label = annos['label']
        sync_entity(cl)
        cl.is_a.append(prop.some(float))

        return cl


def create_variables(onto, variables):
    var_classes = []
    with onto:
        for var, annos in variables.items():
            var_classes.append(create_variable(onto, var, annos))
    return var_classes


def sync_coupled(model, coupled):
    for prop in model.hasInput:
        coupled.hasVariable.append(prop)
    for prop in model.hasOutput:
        coupled.hasVariable.append(prop)


def create_model(onto, model, data, coupled):

    # Creating coupled system
    if type(coupled) == str:
        coupled = types.new_class(coupled, (onto.CoupledSystem,))

    # Creating model
    model = types.new_class(model, (onto.Model,))
    model.label = data['label']
    sync_entity(model)
    model.is_a.append(onto.hasCoupledSystem.some(coupled))

    
    # Inputs
    inputs = data['input']
    for inp in inputs:
        if type(inp) == str:
            model.is_a.append(onto.hasInput.some(onto[inp]))
        if type(inp) == dict:
            model.is_a.append(onto.hasInput.exactly(inp['cardinality'], onto[inp['name']]))

    # Output
    output = data['output']
    model.is_a.append(onto.hasOutput.some(onto[output]))

    sync_coupled(model, coupled)

    return coupled, model


def create_models(onto, models, coupled):
    for model, data in models.items():
        coupled, model = create_model(onto, model, data, coupled)
    return coupled


def create_value(onto, variable, value, coupled_inst):
    cs = onto[coupled_inst]
    prop = onto[f'has{variable}']
    inst = onto[variable]()
    prop[inst] = [value]
    coupled_inst.hasVariable.append(inst)


def create_values(onto, values, coupled_inst):
    for variable, value in values.items():
        if type(value) == list:
            for item in value:
                create_value(onto, variable, item, coupled_inst)
        else:
            create_value(onto, variable, value, coupled_inst)


def sync_inputs(onto, model, coupled):
    with onto:
        for var in onto.hasVariable[coupled]:
            for prop in model.is_a[0].hasInput:
                if var.is_a[0] == prop and var not in model.hasInput:
                    model.hasInput.append(var)


def sync_outputs(coupled, new_var):
    new_vars = []
    var_is = False
    for var in coupled.hasVariable:
        if var.is_a == new_var.is_a:
            new_vars.append(new_var)
            var_is = True
        else:
            new_vars.append(var)
    if not var_is:
        new_vars.append(new_var)
    coupled.hasVariable = new_vars


def run_model(onto, model, foo):
    args = foo.__code__.co_varnames
    arg_vals = []
    for arg in args:
        inputs = model.hasInput
        for inst in inputs:
            inst_types = inst.is_a
            if len(inst_types) == 1:
                inst_type = inst_types[0]
                if inst_type.name == arg:
                    prop = onto[f'has{arg}']
                    prop_vals = prop[inst]
                    if len(prop_vals) == 1:
                        arg_vals.append(prop_vals[0])
    return foo(*arg_vals)
    

def create_model_run(onto, model, coupled_inst, foo):
    model_inst = model()
    model_inst.hasCoupledSystem.append(coupled_inst)
    sync_inputs(onto, model_inst, coupled_inst)
    out_cl = model.hasOutput[0]
    prop = onto[f'has{out_cl.name}']
    out_inst = out_cl()
    prop[out_inst] = [run_model(onto, model_inst, foo)]
    model_inst.hasOutput.append(out_inst)
    sync_outputs(coupled_inst, out_inst)

    
def save_onto(onto, name):
    onto.save(name)
