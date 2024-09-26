from owlready2 import *
import types
from .onto_sync import util_falcon
import os
from collections import Counter


def get_onto(name):
    return get_ontology(name)


def load_onto(path=None):
    """
    Loads an ontology.

    :param path: Path to the ontology file, defaults to None
    :type path: str, optional
    :return: An ontology loaded from the specified file
    :rtype: owlready2.namespace.Ontology
    """
    if not path:
        path = os.path.dirname(os.path.realpath(__file__))
        path = os.path.join(path, 'onto.owl')
    onto = get_ontology(path).load()

    return onto


def sync_entity(entity):
    """
    For a given entity, queries exisiting analogues from Wikidata and
    DBpedia by its label and writes it to the entity's annotation.

    Args:
        entity: An entity from your ontology.
    """
    if len(entity.label) != 1:
        return
    syncs = util_falcon(entity.label[0])
    if syncs:
        if syncs.get('entities_wiki'):
            entity.wikidata = syncs['entities_wiki']
        if syncs.get('entities_db'):
            entity.dbpedia = syncs['entities_db']


def create_variable(onto, name, data, sync=True):
    """
    Creates in an ontology a DataProperty and a class for a variable.

    Args:
        onto (owlready2.namespace.Ontology): Ontology.

        name (str): Name of the variable.

        data (dict): Annotations of the variable.

        sync (bool): If to synchronize a created entity with existing
        knowledge bases.

    Returns:
        onto.Variable: A created class for the variable
    """
    with onto:
        
        # Data Property
        prop = types.new_class(f'has{name}', (DataProperty, FunctionalProperty))
        prop.label = f'has {data["label"].lower()}'
        prop.domain = [onto.Variable]
        prop.range = [float]

        # Class
        cl = types.new_class(name, (onto.Variable,))
        cl.label = data['label']
        cl.is_a.append(prop.some(float))
        if sync:
            sync_entity(cl)
        
        return cl


def create_variables(onto, variables, sync=True):
    """
    Creates in an ontology DataProperties and classes for a list of variables.

    Args:
        onto (owlready2.namespace.Ontology): Ontology.

        variables (dict): A dictionary of variable names with their annotations.

        sync (bool): If to synchronize created entities with existing
        knowledge bases.

    Returns:
        list: A list of created classes for the variables
    """
    var_classes = []
    with onto:
        for var, data in variables.items():
            var_classes.append(create_variable(onto, var, data, sync))

    return var_classes


def create_solver(onto, name, data, sync=True):
    """
    Creates in an ontology a class for a solver.

    Args:
        onto (owlready2.namespace.Ontology): Ontology.

        name (str): Name of the solver.

        data (dict): Annotations of the solver.

        sync (bool): If to synchronize a created entity with existing
        knowledge bases.

    Returns:
        onto.Solver: A created class for the solver.
    """
    with onto:
        cl = types.new_class(name, (onto.Solver,))
        cl.label = data['label']
        for var in data['variables']:
            cl.is_a.append(onto.hasVariable.some(onto[var]))

        if sync:
            sync_entity(cl)

    return cl


def create_solvers(onto, solvers, sync=True):
    """
    Creates in an ontology classes for a list of solvers.

    Args:
        onto (owlready2.namespace.Ontology): Ontology.

        solvers (dict): A dictionary of solvers names with their annotations.

        sync (bool): If to synchronize created entities with existing
        knowledge bases.

    Returns:
        list: A list of created classes for the solvers.
    """
    solv_classes = []
    with onto:
        for solver, data in solvers.items():
            solv_classes.append(create_solver(onto, solver, data, sync))

    return solv_classes


def sync_coupled(model, coupled):
    """
    Synchronizes inputs and outputs of a model with a coupled system.

    Args:
        model (onto.Model): The model.

        coupled (onto.CoupledSystem): The coupled system to synchronize.
    """
    for prop in model.hasInput:
        coupled.hasVariable.append(prop)
    for prop in model.hasOutput:
        coupled.hasVariable.append(prop)


def create_model(onto, name, data, coupled, sync=True):
    """
    Creates in an ontology a class for a model.

    Args:
        onto (owlready2.namespace.Ontology): Ontology.

        name (str): Name of the model.

        data (dict): Annotations of the model.

        coupled (onto.CoupledSystem or str): A coupled system to which the
        model belongs. If str, creates a new class for the coupled system.

        sync (bool): If to synchronize a created entity with existing
        knowledge bases.

    Returns:
        onto.Model: A created class for the model.
    """
    
    # Creating coupled system
    if type(coupled) == str:
        coupled = types.new_class(coupled, (onto.CoupledSystem,))

    # Creating model
    model = types.new_class(name, (onto.Model,))
    model.label = data['label']
    model.is_a.append(onto.hasCoupledSystem.some(coupled))
    if data.get('solver'):
        solver = onto[data['solver']]
        model.is_a.append(onto.hasSolver.some(solver))

    if sync:
        sync_entity(model)
    
    # Inputs
    inputs = data['input']
    for inp in inputs:
        if type(inp) == str:
            model.is_a.append(onto.hasInput.some(onto[inp]))
        if type(inp) == dict:
            model.is_a.append(onto.hasInput.exactly(inp['cardinality'], onto[inp['name']]))

    # Output
    outputs = data['output']
    for out in outputs:
        model.is_a.append(onto.hasOutput.some(onto[out]))

    sync_coupled(model, coupled)

    return coupled, model


def create_models(onto, models, coupled, sync=True):
    """
    Creates in an ontology classes for a list of models.

    Args:
        onto (owlready2.namespace.Ontology): Ontology.

        models (dict): A dictionary of model names with their annotations.

        coupled (onto.CoupledSystem or str): A coupled system to which the
        models belongs. If str, creates a new class for the coupled system.

        sync (bool): If to synchronize created entities with existing
        knowledge bases.

    Returns:
        onto.CoupledSystem: The coupled system to which the models belongs.
    """
    for model, data in models.items():
        coupled, model = create_model(onto, model, data, coupled, sync)
    return coupled


def create_value(onto, variable, value, coupled_inst):
    """
    Creates in an ontology an instance of a variable with its value.

    Args:
        onto (owlready2.namespace.Ontology): Ontology.

        variable (str): Name of the variable class to instanciate.

        value (float): The variable value to specify.

        coupled_inst (onto.CoupledSystem): An instance of a coupled system.
    """
    cs = onto[coupled_inst]
    prop = onto[f'has{variable}']
    inst = onto[variable]()
    prop[inst] = [value]
    coupled_inst.hasVariable.append(inst)


def create_values(onto, values, coupled_inst):
    """
    Creates in an ontology instances of a list of variables with their values.

    Args:
        onto (owlready2.namespace.Ontology): Ontology.

        values (dict): A dictionary of variable names with their values.

        coupled_inst (onto.CoupledSystem): An instance of a coupled system.
    """
    for variable, value in values.items():
        if type(value) == list:
            for item in value:
                create_value(onto, variable, item, coupled_inst)
        else:
            create_value(onto, variable, value, coupled_inst)


def sync_inputs(onto, model_inst, coupled_inst):
    """
    Synchronizes inputs of a coupled system instance with an instance of
    a model.

    Args:
        onto (owlready2.namespace.Ontology): Ontology.

        model_inst (onto.Model): An instance of a model.

        coupled_inst (onto.CoupledSystem): An instance of a coupled system
        to synchronize with.
    """
    with onto:
        for var in onto.hasVariable[coupled_inst]:
            for prop in model_inst.is_a[0].hasInput:
                if var.is_a[0] == prop and var not in model_inst.hasInput:
                    model_inst.hasInput.append(var)


def sync_outputs(coupled_inst, output_var_inst):
    """
    Synchronizes outputs of a coupled system instance with an instance of
    a model output variable.

    Args:
        coupled_inst (onto.CoupledSystem): The instance of a coupled system.

        output_var_inst (onto.Variable): The instance of the model output
        variable.
    """
    new_vars = []
    var_is = False
    for var in coupled_inst.hasVariable:
        if var.is_a == output_var_inst.is_a:
            new_vars.append(output_var_inst)
            var_is = True
        else:
            new_vars.append(var)
    if not var_is:
        new_vars.append(output_var_inst)
    coupled_inst.hasVariable = new_vars


def run_model(onto, model_inst, foo):
    """
    Executed a given function, taken a model inputs as arguments.

    Args:
        onto (owlready2.namespace.Ontology): Ontology.

        model_inst (onto.Model): An instance of a model.

        foo (func): The function to execute.

    Returns:
        A result of the function execution.
    """
    args = foo.__code__.co_varnames
    arg_vals = []
    for arg in args:
        inputs = model_inst.hasInput
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
    """
    Creates a model run and executes a given function.

    Args:
        onto (owlready2.namespace.Ontology): Ontology.

        model (onto.Model): A class of the model to run.

        coupled_inst (onto.CoupledSystem): An instance of a coupled system.

        foo (func): The function to execute.
    """
    model_inst = model()
    model_inst.hasCoupledSystem.append(coupled_inst)
    sync_inputs(onto, model_inst, coupled_inst)
    outputs = model.hasOutput
    if len(outputs) > 0:
        out_cl = outputs[0]
        prop = onto[f'has{out_cl.name}']
        out_inst = out_cl()
        prop[out_inst] = [run_model(onto, model_inst, foo)]
        model_inst.hasOutput.append(out_inst)
        sync_outputs(coupled_inst, out_inst)

    
def save_onto(onto, path=None):
    """
    Saves the ontology into a file.

    Args:
        onto (owlready2.namespace.Ontology): Ontology.

        path (str): Path to the file to save.
    """
    if not path:
        path = os.path.dirname(os.path.realpath(__file__))
        path = os.path.join(path, 'onto.owl')
    onto.save(path, format = 'ntriples')


def export_model_kratos(model):
    """
    Exports a model in a KRATOS format.

    Args:
        model (onto.Model): The model to export.

    Returns:
        dict: A dictionary with the model data in the KRATOS format.
    """
    solver = model.hasSolver[0]

    result = {
        'name': model.label,
        'input_data_list': [],
        'output_data_list': []
        }

    for inp in model.hasInput:
        inp = {
            'data': inp.label[0],
            'from_solver': solver.label[0]
            }
        result['input_data_list'].append(inp)

    return result


def export_coupled_kratos(onto, coupled):
    """
    Exports models from a coupled system in the KRATOS format.

    Args:
        onto (owlready2.namespace.Ontology): Ontology.

        coupled (onto.CoupledSystem): The class for coupled system to export.

    Returns:
        list: A list of models data from the coupled system in KRATOS format.
    """
    result = []
    for model in onto.Model.subclasses():
        if coupled in model.hasCoupledSystem:
            result.append(export_model_for_kratos(model))
    return result


def get_n(onto, type_):
    if type_ == 'class':
        class_ns = list(onto.classes())
    else:
        cl = onto.search_one(label = f'{type_}')
        class_ns = [x.label[0] for x in cl.instances() if len(x.label) > 0]
    if len(class_ns) > 0:
        class_ns = [str(x).split('_') for x in class_ns]
        class_ns = [int(x[-1]) for x in class_ns if len(x) > 0]
        class_ns = sorted(class_ns)
        return class_ns[-1] + 1
    else:
        return 1

    
def get_class(onto, name, parent = None, props = None):
    with onto:
        class_n = get_n(onto, 'class')
        if props:
            classes = onto.search(label = name)
            new_props = []
            for i, prop in enumerate(props):
                if prop == 'data':
                    prop = 'data_'
                new_props.append(prop)
            new_props = set([onto.search_one(label = f'has_{x}') for x in new_props])
            for cl in classes:
                existing_props = set(cl.get_class_properties())
                inter = existing_props.intersection(new_props)
                if len(inter) == len(new_props):
                    return cl
            cl = None
        else:
            cl = onto.search_one(label = name)
        if not cl:
            if parent:
                cl = types.new_class(f'class_{class_n}', (parent,))
            else:
                print(name)
                print(class_n)
                cl = types.new_class(f'class_{class_n}', (Thing,))
            cl.label = name
        return cl


def get_class1(onto, name):
    with onto:
        cl = onto.search_one(label = name)
        if not cl:
            cl = types.new_class(name, (Thing,))
            cl.label = name
        return cl


def get_relation(onto, name, functional = False):
    if name == 'data':
        name = 'data_'
    name = f'has_{name}'
    with onto:
        rel = onto.search_one(label = name)
        if not rel:
            if functional:
                rel = types.new_class(name, (ObjectProperty, FunctionalProperty))
            else:
                rel = types.new_class(name, (ObjectProperty,))
            rel.label = name
        return rel


def get_property(onto, name, functional = False):
    name = f'has_{name}'
    with onto:
        prop = onto.search_one(label = name)
        if not prop:
            if functional:
                prop = types.new_class(name, (DataProperty, FunctionalProperty))
            else:
                prop = types.new_class(name, (DataProperty,))
            prop.label = name
        return prop


def dict2class(onto, coupled_system_name, inst, pred_name, obj_data, obj_sup_cl = None, functional = False, i = None):
    if i:
        class_name = f'{pred_name}{i}'
    else:
        class_name = pred_name
    with onto:
        if obj_sup_cl:
            obj_cl = get_class(onto, class_name, coupled_system_name, obj_sup_cl)
        else:
            obj_cl = get_class(onto, pred_name, coupled_system_name)
        rel = get_relation(onto, pred_name, functional)
        obj_inst = obj_cl()
        for inst_pred_name, inst_obj_data in obj_data.items():
            obj_inst = add_statement(onto, coupled_system_name, obj_inst, inst_pred_name, inst_obj_data)
            if obj_inst not in rel[inst]:
                print('dict', inst, rel, obj_inst)
                rel[inst].append(obj_inst)


def add_statement(onto, inst, pred_name, obj_data):
    with onto:
        if type(obj_data) == dict and all([type(obj_value) == dict for obj_key, obj_value in obj_data.items()]):
            rel = get_relation(onto, pred_name)
            for obj_key, obj_value in obj_data.items():
                obj_cl = get_class(onto, pred_name, props=obj_value.keys())
                obj_cl_label = obj_cl.label[0]
                inst_n = get_n(onto, obj_cl_label)
                obj_inst = obj_cl(f'{obj_cl_label}_{inst_n}')
                obj_inst.label = f'{obj_cl_label}_{inst_n}'
                for inst_pred_name, inst_obj_data in obj_value.items():
                    obj_inst = add_statement(onto, obj_inst, inst_pred_name, inst_obj_data)
                    if obj_inst not in rel[inst]:
                        print('dict_dict', inst, rel, obj_inst)
                        rel[inst].append(obj_inst)
            for inst_cl in inst.is_a:
                ks = dict(Counter([obj_inst.is_a[0] for obj_inst in rel[inst]]))
                for t, k in ks.items():
                    if k == 1:
                        inst_cl.is_a.append(rel.some(t))
                    else:
                        inst_cl.is_a.append(rel.exactly(k, t))
        elif type(obj_data) == dict:
            obj_cl = get_class(onto, pred_name, props=obj_data.keys())
            rel = get_relation(onto, pred_name, True)
            obj_cl_label = obj_cl.label[0]
            inst_n = get_n(onto, obj_cl_label)
            obj_inst = obj_cl(f'{obj_cl_label}_{inst_n}')
            obj_inst.label = f'{obj_cl_label}_{inst_n}'
            for inst_pred_name, inst_obj_data in obj_data.items():
                obj_inst = add_statement(onto, obj_inst, inst_pred_name, inst_obj_data)
                if obj_inst not in rel[inst]:
                    print('dict', inst, rel, obj_inst)
                    rel[inst].append(obj_inst)
            #dict2class(onto, coupled_system_name, inst, pred_name, obj_data, None, True)
            for inst_cl in inst.is_a:
                ks = dict(Counter([obj_inst.is_a[0] for obj_inst in rel[inst]]))
                for t, k in ks.items():
                    if k == 1:
                        inst_cl.is_a.append(rel.some(t))
                    else:
                        inst_cl.is_a.append(rel.exactly(k, t))
        elif type(obj_data) == list:
            for i, obj_item in enumerate(obj_data):
                if type(obj_item) == dict:
                    obj_cl = get_class(onto, pred_name)
                    rel = get_relation(onto, pred_name)
                    obj_cl_label = obj_cl.label[0]
                    inst_n = get_n(onto, obj_cl_label)
                    obj_inst = obj_cl(f'{obj_cl_label}_{inst_n}')
                    obj_inst.label = f'{obj_cl_label}_{inst_n}'
                    for inst_pred_name, inst_obj_data in obj_item.items():
                        obj_inst = add_statement(onto, obj_inst, inst_pred_name, inst_obj_data)
                        if obj_inst not in rel[inst]:
                            print('list_dict', inst, rel, obj_inst)
                            rel[inst].append(obj_inst)
                    #dict2class(onto, coupled_system_name, inst, pred_name, obj_item, obj_sup_cl, i)
                else:
                    prop = get_property(onto, pred_name)
                    if obj_item not in prop[inst]:
                        print('list_literal', inst, prop, obj_item)
                        prop[inst].append(obj_item)
            rel = get_relation(onto, pred_name)
            for inst_cl in inst.is_a:
                if all([type(obj_item) == dict for obj_item in obj_data]):
                    ks = dict(Counter([obj_inst.is_a[0] for obj_inst in rel[inst]]))
                    for t, k in ks.items():
                        if k == 1:
                            inst_cl.is_a.append(rel.some(t))
                        else:
                            inst_cl.is_a.append(rel.exactly(k, t))
                else:
                    prop = get_property(onto, pred_name)
                    ks = dict(Counter([type(obj_item) for obj_item in obj_data]))
                    for t, k in ks.items():
                        if k == 1:
                            inst_cl.is_a.append(prop.some(t))
                        else:
                            inst_cl.is_a.append(prop.exactly(k, t))
        else:
            prop = get_property(onto, pred_name, True)
            if obj_data not in prop[inst]:
                print('literal', inst, prop, obj_data)
                prop[inst].append(obj_data)
                for cl in inst.is_a:
                    k = len(prop[inst])
                    if k == 1:
                        cl.is_a.append(prop.some(type(obj_data)))
                    else:
                        cl.is_a.append(prop.exactly(k, type(obj_data)))
    return inst


def add_triple(onto, inst, pred_name, obj_data):
    with onto:
        if type(obj_data) == dict and all([type(obj_value) == dict for obj_key, obj_value in obj_data.items()]):
            rel = get_relation(onto, pred_name)
            for obj_key, obj_value in obj_data.items():
                obj_cl = get_class1(onto, pred_name)
                obj_inst = obj_cl()
                for inst_pred_name, inst_obj_data in obj_value.items():
                    obj_inst = add_triple(onto, obj_inst, inst_pred_name, inst_obj_data)
                    if obj_inst not in rel[inst]:
                        print('dict_dict', inst, rel, obj_inst)
                        rel[inst].append(obj_inst)
        elif type(obj_data) == dict:
            obj_cl = get_class1(onto, pred_name)
            rel = get_relation(onto, pred_name, True)
            obj_inst = obj_cl()
            for inst_pred_name, inst_obj_data in obj_data.items():
                obj_inst = add_triple(onto, obj_inst, inst_pred_name, inst_obj_data)
                if obj_inst not in rel[inst]:
                    print('dict', inst, rel, obj_inst)
                    rel[inst].append(obj_inst)
        elif type(obj_data) == list:
            for i, obj_item in enumerate(obj_data):
                if type(obj_item) == dict:
                    obj_cl = get_class1(onto, pred_name)
                    rel = get_relation(onto, pred_name)
                    obj_inst = obj_cl()
                    for inst_pred_name, inst_obj_data in obj_item.items():
                        obj_inst = add_triple(onto, obj_inst, inst_pred_name, inst_obj_data)
                        if obj_inst not in rel[inst]:
                            print('list_dict', inst, rel, obj_inst)
                            rel[inst].append(obj_inst)
                else:
                    prop = get_property(onto, pred_name)
                    if obj_item not in prop[inst]:
                        print('list_literal', inst, prop, obj_item)
                        prop[inst].append(obj_item)
        else:
            prop = get_property(onto, pred_name, True)
            if obj_data not in prop[inst]:
                print('literal', inst, prop, obj_data)
                prop[inst].append(obj_data)

    return inst


def infer_axioms(onto):
    for inst in onto.individuals():
        new_props = set(inst.get_properties())
        cl = type(inst)
        match = False
        for sub_cl in cl.subclasses():
            old_props = set([x.property for x in sub_cl.equivalent_to])
            if old_props == new_props:
                #inst.is_a = [sub_cl]
                match = True
        if not match:
            new_cl = types.new_class(f'{cl.name}_{inst.name}', (cl,))
            #inst.is_a = [new_cl]
            for rel in inst.get_properties():
                for obj in rel[inst]:
                    new_cl.equivalent_to.append(rel.some(type(obj)))


def import_coupled_kratos(onto, data, label):
    with onto:
        coupled_system = get_class1(onto, 'coupled_system')
        inst = coupled_system(label)
        for pred_name, obj_data in data.items():
            inst = add_triple(onto, inst, pred_name, obj_data)
        infer_axioms(onto)
