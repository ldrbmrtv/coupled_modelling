from owlready2 import *
import types
import os
from collections import Counter


def load_onto(path=None):
    """
    Loads an ontology.

    Args:
        path (str, optional): Path to the ontology file, if None the default ontology is used.

    Returns:
        The loaded ontology
    """
    if not path:
        path = os.path.dirname(os.path.realpath(__file__))
        path = os.path.join(path, 'onto.owl')
    onto = get_ontology(path).load()

    return onto


def save_onto(path=None):
    """
    Saves the ontology into a file.

    Args:
        path (str): Path to the file to save.
    """
    if not path:
        path = os.path.dirname(os.path.realpath(__file__))
        path = os.path.join(path, 'onto.owl')
    onto.save(path, format = 'ntriples')


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


def add_coupled_system(inst, pred_name, obj_data, coupled_system):
    """
    Creates a coupled system with given data.

    Args:
        inst (OWL instance): OWL-instance.
        pred_name (str): A property name from the data.
        obj_data: Value of the property from the data.
        coupled_system (OWL instance): OWL-instance of the coupled system class.
    """
    with onto:
        if type(obj_data) == dict and all([type(obj_value) == dict for obj_key, obj_value in obj_data.items()]):
            rel = get_relation(pred_name)
            for obj_key, obj_value in obj_data.items():
                obj_cl = get_class(pred_name)
                obj_inst = obj_cl()
                obj_inst.label = obj_key
                for inst_pred_name, inst_obj_data in obj_value.items():
                    obj_inst = add_coupled_system(obj_inst, inst_pred_name, inst_obj_data, coupled_system)
                    if obj_inst not in rel[inst]:
                        print('dict_dict', inst, rel, obj_inst)
                        rel[inst].append(obj_inst)
        elif type(obj_data) == dict:
            obj_cl = get_class(pred_name)
            rel = get_relation(pred_name, True)
            obj_inst = obj_cl()
            for inst_pred_name, inst_obj_data in obj_data.items():
                obj_inst = add_coupled_system(obj_inst, inst_pred_name, inst_obj_data, coupled_system)
                if obj_inst not in rel[inst]:
                    print('dict', inst, rel, obj_inst)
                    rel[inst].append(obj_inst)
        elif type(obj_data) == list:
            for i, obj_item in enumerate(obj_data):
                if type(obj_item) == dict:
                    obj_cl = get_class(pred_name)
                    rel = get_relation(pred_name)
                    obj_inst = obj_cl()
                    for inst_pred_name, inst_obj_data in obj_item.items():
                        obj_inst = add_coupled_system(obj_inst, inst_pred_name, inst_obj_data, coupled_system)
                        if obj_inst not in rel[inst]:
                            print('list_dict', inst, rel, obj_inst)
                            rel[inst].append(obj_inst)
                else:
                    prop = get_property(pred_name)
                    if obj_item not in prop[inst]:
                        print('list_literal', inst, prop, obj_item)
                        prop[inst].append(obj_item)
        else:
            prop = get_property(pred_name, True)
            if obj_data not in prop[inst]:
                print('literal', inst, prop, obj_data)
                prop[inst].append(obj_data)

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
        inst = coupled_system()
        inst.label = label
    return inst


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
    for x in cl.equivalent_to:
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
        try:
            props[prop.name] = [x.name for x in prop[inst]]
        except:
            props[prop.name] = prop[inst]
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


def add_value(subj, prop, value=None):
    """
    Adds a value to the given subject and property.

    Args:
        subj (OWL instance): An instance that is the subject of the statement.
        prop (str): Label of the property.
        value (optional): value to add. If None, a new instance is created.

    Returns:
        The value, useful if the new instance is created.
    """
    if prop == 'label':
        subj.label = value
        return value
    prop = onto.search_one(label = prop)
    with onto:
        if not value:
            cl = get_class(prop.name.replace('has_', ''))
            value = cl()
        prop[subj].append(value)
    return value


def delete_value(subj, prop, value=[]):
    """
    Deletes a value from the given subject and property.

    Args:
        subj (OWL instance): An instance that is the subject of the statement.
        prop (str): Label of the property.
        value (optional): value to delete. If not specified, all values are removed.
    """
    if prop == 'label':
        subj.label = value
    prop = onto.search_one(label = prop)
    with onto:
        if value == []:
            prop[subj] = []
        else:
            prop[subj].remove(value)


def replace_value(subj, prop, new_value, old_value=[]):
    """
    Replace a value from the given subject and property.

    Args:
        subj (OWL instance): An instance that is the subject of the statement.
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


def copy_instance(inst_name):
    """
    Creates a structural copy of a given instance with all its properties.

    Args:
        inst_name (str): Instance name.

    Returns:
        Created instance.
    """
    inst = onto[inst_name]
    cl = type(inst)
    new_inst = cl()
    for prop in inst.get_properties():
        objects = prop[inst]
        for obj in objects:
            if hasattr(obj, 'name'):
                cl = type(obj)
                obj = cl()
            prop[new_inst].append(obj)
    return new_inst


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
    new_inst = cl()
    for prop in inst.get_properties():
        objects = prop[inst]
        for obj in objects:
            if hasattr(obj, 'name'):
                cl = type(obj)
                obj = copy_instance_recursively(obj.name)
            prop[new_inst].append(obj)
    return new_inst


def export_coupled_kratos(coupled_system_name):
    """
    Returns a coupled system in Kratos format.

    Args:
        coupled_system_name (str): Name of the coupled system.

    Returns:
        Dictionary of nested properties.
    """
    props = get_instance_properties(coupled_system_name)
    label = None
    for key in list(props.keys()):
        props[key.replace('has_', '')] = props.pop(key)
        if key == 'label':
            label = props['label'][0]
        if key == 'has_data_':
            props['data'] = props.pop('data_')
    if label:
        props.pop('label', None)
    if str(type(onto[coupled_system_name]).name).startswith('coupled_system'):
        label = None
    for key, items in props.items():
        if len(items) > 1 and key in ['solvers', 'data']:
            temp_dict = {}
            for item in items:
                obj_props = export_coupled_kratos(item)
                temp_dict[list(obj_props.keys())[0]] = list(obj_props.values())[0]
            props[key] = temp_dict
        elif len(items) > 1 or key in [
            'convergence_accelerators',
            'convergence_criteria',
            'input_data_list',
            'output_data_list',
            'export_data',
            'import_data',
            'import_meshes'
        ]:
            temp_list = []
            for item in items:
                if onto[item]:
                    temp_list.append(export_coupled_kratos(item))
                else:
                    temp_list.append(item)
            props[key] = temp_list
        else:
            print(key, items)
            item = items[0]
            if onto[item]:
                props[key] = export_coupled_kratos(item)
            else:
                props[key] = item
    if label:
        props = {label: props}
    label = None
    return props


def get_linked_instances(inst_name, insts):
    """
    For a given instance, returns its connected instances.

    Args:
        inst_name (str): Instance name.
        insts (list): List of instances

    Returns:
        A list of connected instance names.
    """
    inst = onto[inst_name]
    insts.append(inst)
    for prop in inst.get_properties():
        for value in prop[inst]:
            if hasattr(value, 'name'):
                get_linked_instances(value.name, insts)


def infer_axioms(coupled_system):
    """
    Infers new classes and axioms from a given coupled system.

    Args:
        coupled_system (OWL instance): OWL-instance of the coupled system class.
    """
    insts = []
    get_linked_instances(coupled_system, insts)

    for inst in insts:
        new_props = []
        for rel in inst.get_properties():
            if str(rel) == 'rdf-schema.label':
                continue
            for obj in rel[inst]:
                new_props.append(rel)
        new_props = Counter(new_props)
        cl = type(inst)
        match = False
        for sub_cl in cl.subclasses():
            old_props = dict([(x.property, x.cardinality) for x in sub_cl.equivalent_to])
            old_props.pop('rdf-schema.label', None)
            if old_props == new_props:
                match = True
                inst.is_a = [sub_cl]
                break
        if not match:
            new_cl = types.new_class(f'{cl.name}_{inst.name}', (cl,))
            for rel, card in new_props.items():
                for obj in rel[inst]:
                    new_cl.equivalent_to.append(rel.exactly(card, type(obj)))
            inst.is_a = [new_cl]


def import_coupled_kratos(data, label):
    """
    Recursively creates an OWL-instance of the coupled system class with given data and label.

    Args:
        data: Dictionary with the coupled system data.
        label: Label of the coupled system.

    Returns:
        The OWL-instance of the coupled system.
    """
    inst = create_coupled(label)
    for pred_name, obj_data in data.items():
        inst = add_coupled_system(inst, pred_name, obj_data, inst)
    infer_axioms(inst.name)


onto = load_onto()
