from owlready2 import *
import types
import os
from collections import Counter


def get_onto_path():
    path = os.path.dirname(os.path.realpath(__file__))
    path = os.path.join(path, 'onto.owl')
    
    return path


def new_onto():
    onto = default_world.get_ontology(onto_uri)
    
    return onto


def load_onto():
    """
    Loads an ontology.

    Returns:
        Loaded ontology
    """
    onto = default_world.get_ontology(onto_uri).load()
    
    return onto


def save_onto():
    """
    Saves the ontology.

    """
    default_world.save()


def save_locally():
    """
    Saves the ontology into a file.

    """
    onto.save(get_onto_path())


def get_class(name):
    """
    Gets or creates an OWL-class with a given name, which is used as the class URI and its label.

    Args:
        name (str): Name of the class.
    """
    with onto:
        cl = onto.search_one(label = name)
        if not cl:
            cl = types.new_class(name, (Thing,))
            cl.label = name
        return cl


def get_relation(name, functional = False):
    """
    Gets or creates an ObjectProperty with a given name.

    Args:
        name (str): Name of the ObjectProperty.
        functional (bool, optional): if the ObjectProperty is functional.
    """
    #if name == 'data':
    #    name = 'data_'
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


def get_property(name, functional = False):
    """
    Gets or creates a DataProperty with a given name.

    Args:
        name (str): Name of the DataProperty.
        functional (bool, optional): if the DataProperty is functional.
    """
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


def instance_name():
    n = len(list(onto.individuals())) + 1
    return f'instance_{n}'


def has_only_label(inst):
    props = list(inst.get_properties())
    props = [x.name for x in props]
    return props == ['label']


def dict_to_inst(inst, pred_name, data, functional=False):
    obj_cl = get_class(pred_name)
    rel = get_relation(pred_name, functional)
    obj_inst = obj_cl(instance_name())
    for inst_pred_name, inst_obj_data in data.items():
        obj_inst = add_coupled_system(obj_inst, inst_pred_name, inst_obj_data)
        if obj_inst not in rel[inst]:
            print('dict', inst, rel, obj_inst)
            rel[inst].append(obj_inst)


def str_to_inst(inst, pred_name, label, functional=False):
    obj_cl = get_class(pred_name)
    rel = get_relation(pred_name, functional)
    res = onto.search(label = label)
    obj_inst = None
    for item in res:
        if has_only_label(item):
            obj_inst = item
            break
    if obj_inst:
        if not obj_cl in obj_inst.is_a:
            obj_inst.is_a.append(obj_cl)
    else:
        obj_inst = obj_cl(instance_name())
        obj_inst.label = [label]
    if obj_inst not in rel[inst]:
        print('str', inst, rel, obj_inst)
        rel[inst].append(obj_inst)


def num_to_literal(inst, pred_name, num, functional=False):
    prop = get_property(pred_name, functional)
    if num not in prop[inst]:
        print('num', inst, prop, num)
        prop[inst].append(num)


def add_coupled_system(inst, pred_name, obj_data):
    """
    Creates a coupled system with given data.

    Args:
        inst (OWL instance): OWL-instance.
        pred_name (str): A property name from the data.
        obj_data: Value of the property from the data.
    """
    with onto:
        if type(obj_data) == dict and all([type(obj_value) == dict for obj_key, obj_value in obj_data.items()]):
            rel = get_relation(pred_name)
            for obj_key, obj_value in obj_data.items():
                obj_cl = get_class(pred_name)
                #obj_inst = onto.search_one(label = obj_key)
                #if obj_inst:
                #    if not obj_cl in obj_inst.is_a:
                #        obj_inst.is_a.append(obj_cl)
                #else:
                obj_inst = obj_cl(instance_name())
                obj_inst.label = obj_key
                for inst_pred_name, inst_obj_data in obj_value.items():
                    obj_inst = add_coupled_system(obj_inst, inst_pred_name, inst_obj_data)
                    if obj_inst not in rel[inst]:
                        print('dict_dict', inst, rel, obj_inst)
                        rel[inst].append(obj_inst)
        elif type(obj_data) == dict:
            dict_to_inst(inst, pred_name, obj_data)
        elif type(obj_data) == list:
            for i, obj_item in enumerate(obj_data):
                if type(obj_item) == dict:
                    dict_to_inst(inst, pred_name, obj_item)
                elif type(obj_item) == str:
                    str_to_inst(inst, pred_name, obj_item)
                else:
                    num_to_literal(inst, pred_name, obj_item)
        elif type(obj_data) == str:
            str_to_inst(inst, pred_name, obj_data)
        else:
            num_to_literal(inst, pred_name, obj_data, True)

    return inst


def create_coupled(label):
    """
    Creates an OWL-instance of the coupled system class with a given label.

    Args:
        label (str): Label for the coupled system.

    Returns:
        An OWL instance for the coupled system
    """
    with onto:
        coupled_system = get_class('coupled_system')
        inst = coupled_system(instance_name())
        inst.label = label
    return inst.name


def get_class_properties(class_name):
    """
    For a given class, returns a dictionary of its axioms.

    Args:
        class_name (str): Class name.

    Returns:
        The dictionary of the class axioms.
    """
    cl = onto[class_name]
    props = []
    for x in cl.is_a:
        if hasattr(x, 'property'):
            try:
                props.append((x.property.name, {'cardinality': x.cardinality, 'type': x.value.name}))
            except:
                props.append((x.property.name, {'cardinality': x.cardinality, 'type': x.value}))
    props = dict(props)
    props.pop('label', None)
    return props


def get_subclasses(class_label):
    """
    For a given class, returns its subclasses.

    Args:
        class_label (str): Class label.

    Returns:
        A list of the subclass names.
    """
    cl = onto.search_one(label = class_label)
    return [x.name for x in cl.subclasses()]


def get_instance_properties(inst_name):
    """
    For a given instance, returns its statements.

    Args:
        inst_name (str): Instance name.

    Returns:
        A dictionary of instance properties and their values.
    """
    inst = onto[inst_name]
    props = {}
    for prop in inst.get_properties():
        temp = []
        for obj in prop[inst]:
            if hasattr(obj, 'name'):
                temp.append(obj.name)
            else:
                temp.append(obj)
            props[prop.name.replace('has_', '')] = temp
    return props

    
def get_instances(class_label):
    """
    For a given class, returns its instances.

    Args:
        class_label (str): Class label.

    Returns:
        A list of class instance names.
    """
    cl = onto.search_one(label = class_label)
    return [x.name for x in cl.instances()]


def get_values(subj, prop):
    """
    Returns a property for the given subject .

    Args:
        subj (str): A name of the instance that is the subject of the statement.
        prop (str): Label of the property.

    Returns:
        The value.
    """
    subj = onto[subj]
    prop = onto[f'has_{prop}']
    values = prop[subj]
    res = []
    for value in values:
        if hasattr(value, 'name'):
            res.append(value.name)
        else:
            res.append(value)
    return res

    
def add_value(subj, prop_name, value=None):
    """
    Adds a value to the given subject and property.

    Args:
        subj (str): A name of the instance that is the subject of the statement.
        prop (str): Label of the property.
        value (optional): value to add. If None, a new instance is created.

    Returns:
        The value, useful if the new instance is created.
    """
    subj = onto[subj]
    if onto[value]:
        value = onto[value]
    
    if prop_name == 'label':
        subj.label = value
        return value

    with onto:
        if not value:
            cl = get_class(prop_name)
            value = cl(instance_name())
            prop = get_relation(prop_name)
            prop[subj].append(value)
        elif type(value) == str:
            if value.startswith('instance'):
                prop = get_relation(prop_name)
                prop[subj].append(value)
            else:
                value = str_to_inst(subj, prop_name, value)
        else:
            prop = get_property(prop_name)
            prop[subj].append(value)
    if hasattr(value, 'name'):
        return value.name


def delete_value(subj, prop, value=[]):
    """
    Deletes a value from the given subject and property.

    Args:
        subj (str): A name of the instance that is the subject of the statement.
        prop (str): Label of the property.
        value (optional): value to delete. If not specified, all values are removed.
    """
    subj = onto[subj]
    if onto[value]:
        value = onto[value]
    
    if prop == 'label':
        if value == []:
            subj.label = []
        else:
            subj.label.remove(value)
        return
    prop = onto.search_one(label = f'has_{prop}')
    with onto:
        if value == []:
            print(subj, prop)
            prop[subj] = []
        else:
            prop[subj].remove(value)


def replace_value(subj, prop, new_value, old_value=[]):
    """
    Replace a value from the given subject and property.

    Args:
        subj (str): A name of the instance that is the subject of the statement.
        prop (str): Label of the property.
        new_value: new value to add.
        old_value (optional): old value to delete. If not specified, all values are removed.
    """
    delete_value(subj, prop, old_value)
    add_value(subj, prop, new_value)


def get_instance_properties_recursively(inst_name):
    """
    Get instance properties and its subproperties recursively.

    Args:
        inst_name (str): Instance name.

    Returns:
        Dictionary of nested properties.
    """
    props = get_instance_properties(inst_name)
    for key, items in props.items():
        temp_list = []
        for item in items:
            if onto[item]:
                temp_list.append(get_instance_properties_recursively(item))
            else:
                temp_list.append(item)
        props[key] = temp_list
    return props


def create_instance(prop, parent, data=None):
    inst = add_value(parent, prop)
    if data:
        for prop, value in data.items():
            add_value(inst, prop, value)
    return inst


def copy_instance(inst, parent=None, data=None):
    """
    Creates a structural copy of a given instance with all its properties.

    Args:
        inst_name (str): Instance name.
        parent_name (str, optional): Name of the parent instance.

    Returns:
        Created instance.
    """
    #print(inst)
    inst = onto[inst]
    cl = type(inst)
    #print(inst, cl)
    new_inst = cl(instance_name())
    if parent:
        parent = onto[parent]
        for subj, prop in inst.get_inverse_properties():
            if type(subj) == cl:
                break
        prop[parent].append(new_inst)
    new_props = data.keys()
    for prop in inst.get_properties():
        if prop.name.replace('has_', '') in new_props:
            continue
        objects = prop[inst]
        for obj in objects:
            if hasattr(obj, 'name'):
                if not has_only_label(obj):
                    continue
            prop[new_inst].append(obj)
    if data:
        for prop, value in data.items():
            #onto_prop = get_property(prop)
            #if onto_prop[new_inst]:
            #    replace_value(new_inst.name, prop, value)
            #else:
            add_value(new_inst.name, prop, value)
    return new_inst.name


def copy_instance_recursively(inst_name):
    """
    Creates a structural copy of a given instance with all it properties revursively.

    Args:
        inst_name (str): Instance name.

    Returns:
        Created instance.
    """
    inst = onto[inst_name]
    cl = type(inst)
    new_inst = cl(instance_name())
    for prop in inst.get_properties():
        objects = prop[inst]
        for obj in objects:
            if hasattr(obj, 'name'):
                cl = type(obj)
                obj = copy_instance_recursively(obj.name)
                obj = onto[obj]
            prop[new_inst].append(obj)
    return new_inst.name


def export_coupled_kratos(coupled_system):
    """
    Returns a coupled system in Kratos format.

    Args:
        coupled_system_name (str): Name of the coupled system.

    Returns:
        Dictionary of nested properties.
    """
    props = get_instance_properties(coupled_system)
    label = None
    for key in list(props.keys()):
        if key == 'label':
            label = props['label'][0]
        #if key == 'data_':
        #    props['data'] = props.pop('data_')
    if label:
        props.pop('label', None)
    if 'coupled_system' in str(type(onto[coupled_system]).name):
        label = None
    for key, items in props.items():
        if len(items) > 1 and key in force_dict():
            temp_dict = {}
            for item in items:
                obj_props = export_coupled_kratos(item)
                temp_dict[list(obj_props.keys())[0]] = list(obj_props.values())[0]
            props[key] = temp_dict
        elif len(items) > 1 or key in force_list():
            temp_list = []
            for item in items:
                if onto[item]:
                    if has_only_label(onto[item]):
                        temp_list.append(onto[item].label[0])
                    else:
                        temp_list.append(export_coupled_kratos(item))
                else:
                    temp_list.append(item)
            props[key] = temp_list
        else:
            #print(key, items)
            item = items[0]
            if onto[item]:
                if has_only_label(onto[item]):
                    props[key] = onto[item].label[0]
                else:
                    props[key] = export_coupled_kratos(item)
            else:
                props[key] = item
    if label:
        props = {label: props}
    label = None
    return props


def force_dict():
    return ['solvers', 'data']


def force_list():
    return [
        'convergence_accelerators',
        'convergence_criteria',
        'input_data_list',
        'output_data_list',
        'export_data',
        'import_data',
        'import_meshes',
        'data_transfer_operator_options'
    ]


def get_connected_instances_recursively(inst_name, insts, depth):
    """
    For a given instance, returns its connected instances.

    Args:
        inst_name (str): Instance name.
        insts (list): List of instances.
        depth (int): Depth of the instance tree.

    Returns:
        A list of connected instance names.
    """
    inst = onto[inst_name]
    #if insts.get(inst):
    #    if insts[inst] > depth:
    #        pass
    #    else:
    #        insts[inst] = depth
    #else:
    insts[inst] = depth
    depth += 1
    for prop in inst.get_properties():
        for value in prop[inst]:
            if hasattr(value, 'name'):
                get_connected_instances_recursively(value.name, insts, depth)


def infer_class_properties(inst):
    """
    Infers new classes and axioms from a given instance.

    Args:
        inst (OWL instance): OWL-instance to infer from.
    """
    new_props = []
    for rel in inst.get_properties():
        if str(rel) == 'rdf-schema.label':
            continue
        for obj in rel[inst]:
            if hasattr(obj, 'is_a'):
                new_props.append((rel, And(obj.is_a)))
            else:
                new_props.append((rel, type(obj)))
    new_props = Counter(new_props)
    if not(len(new_props)):
        return
    new_classes = []
    for cl in inst.is_a:
        match = False
        subclasses = list(cl.subclasses())
        #subclasses.append(cl)
        for sub_cl in subclasses:
            old_props = {}
            for x in sub_cl.is_a:
                if hasattr(x, 'property') and hasattr(x, 'value'):
                    old_props[(x.property, x.value)] = x.cardinality
            #old_props.pop('rdf-schema.label', None)
            if old_props == new_props:
                match = True
                if sub_cl not in inst.is_a:
                    new_classes.append(sub_cl)
                break
        if not match:
            n = len(list(cl.subclasses())) + 1
            new_cl = types.new_class(f'{cl.name}_{n}', (cl,))
            for (rel, obj_cl), card in new_props.items():
                new_cl.is_a.append(rel.exactly(card, obj_cl))
            #inst.is_a.remove(cl)
            new_classes.append(new_cl)
    inst.is_a = new_classes


def infer_class_properties_recursively(insts):
    max_depth = max([x for x in insts.values()])
    for inst, depth in list(insts.items()):
        if depth == max_depth:
            infer_class_properties(inst)
            del insts[inst]
    if len(insts):
        infer_class_properties_recursively(insts)


def infer_coupled_system_structure(coupled_system):
    insts = {}
    get_connected_instances_recursively(coupled_system, insts, 0)
    infer_class_properties_recursively(insts)


def import_coupled_kratos(data, label):
    """
    Recursively creates an OWL-instance of the coupled system class with given data and label.

    Args:
        data: Dictionary with the coupled system data.
        label: Label of the coupled system.

    Returns:
        The OWL-instance of the coupled system.
    """
    inst_name = create_coupled(label)
    inst = onto[inst_name]
    for pred_name, obj_data in data.items():
        inst = add_coupled_system(inst, pred_name, obj_data)
    infer_coupled_system_structure(inst_name)
    return inst_name


onto_uri = 'http://coupled_modelling.owl'
default_world.set_backend(filename = 'db.sqlite3')
try:
    onto = load_onto()
except:
    onto = new_onto()
