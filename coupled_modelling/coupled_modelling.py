from owlready2 import *
import types
from .onto_sync import util_falcon
import os


def load_onto(path=None):
    """
    Loads an ontology.

    Args:
        path (str): Path to the ontology file. If no path is given, returns the empty coupled model ontology.

    Returns:
        owlready2.namespace.Ontology: An ontology loaded from the specified file.
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

    
def save_onto(onto, path):
    """
    Saves the ontology into a file.

    Args:
        onto (owlready2.namespace.Ontology): Ontology.

        path (str): Path to the file to save.
    """
    onto.save(path)


def export_model_for_kratos(model):
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


def export_coupled_for_kratos(onto, coupled):
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
