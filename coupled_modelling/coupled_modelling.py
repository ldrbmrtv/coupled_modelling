from owlready2 import *
import types
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


def get_class(onto, name):
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


def specify_coupled_system(onto, inst, coupled_system):
    prop = get_relation(onto, 'coupled_system', True)
    prop[inst] = [coupled_system]


def add_coupled_system(onto, inst, pred_name, obj_data, coupled_system):
    with onto:
        if type(obj_data) == dict and all([type(obj_value) == dict for obj_key, obj_value in obj_data.items()]):
            rel = get_relation(onto, pred_name)
            for obj_key, obj_value in obj_data.items():
                obj_cl = get_class(onto, pred_name)
                obj_inst = obj_cl()
                specify_coupled_system(onto, obj_inst, coupled_system)
                for inst_pred_name, inst_obj_data in obj_value.items():
                    obj_inst = add_coupled_system(onto, obj_inst, inst_pred_name, inst_obj_data, coupled_system)
                    if obj_inst not in rel[inst]:
                        print('dict_dict', inst, rel, obj_inst)
                        rel[inst].append(obj_inst)
        elif type(obj_data) == dict:
            obj_cl = get_class(onto, pred_name)
            rel = get_relation(onto, pred_name, True)
            obj_inst = obj_cl()
            specify_coupled_system(onto, obj_inst, coupled_system)
            for inst_pred_name, inst_obj_data in obj_data.items():
                obj_inst = add_coupled_system(onto, obj_inst, inst_pred_name, inst_obj_data, coupled_system)
                if obj_inst not in rel[inst]:
                    print('dict', inst, rel, obj_inst)
                    rel[inst].append(obj_inst)
        elif type(obj_data) == list:
            for i, obj_item in enumerate(obj_data):
                if type(obj_item) == dict:
                    obj_cl = get_class(onto, pred_name)
                    rel = get_relation(onto, pred_name)
                    obj_inst = obj_cl()
                    specify_coupled_system(onto, obj_inst, coupled_system)
                    for inst_pred_name, inst_obj_data in obj_item.items():
                        obj_inst = add_coupled_system(onto, obj_inst, inst_pred_name, inst_obj_data, coupled_system)
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


def infer_axioms(onto, coupled_system):
    insts = onto.search(has_coupled_system = coupled_system)
    insts.append(coupled_system)
    for inst in insts:
        new_props = []
        for rel in inst.get_properties():
            for obj in rel[inst]:
                new_props.append(rel)
        new_props = Counter(new_props)
        cl = type(inst)
        match = False
        for sub_cl in cl.subclasses():
            old_props = dict([(x.property, x.cardinality) for x in sub_cl.equivalent_to])
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


def create_coupled(onto, label):
    with onto:
        coupled_system = get_class(onto, 'coupled_system')
        inst = coupled_system()
        inst.label = label
    return inst


def import_coupled_kratos(onto, data, label):
    inst = create_coupled(onto, label)
    for pred_name, obj_data in data.items():
        inst = add_coupled_system(onto, inst, pred_name, obj_data, inst)
    infer_axioms(onto, inst)


def get_class_properties(onto, class_name):
    cl = onto[class_name]
    props = []
    for x in cl.equivalent_to:
        try:
            props.append((x.property.name, {'cardinality': x.cardinality, 'type': x.value.name}))
        except:
            props.append((x.property.name, {'cardinality': x.cardinality, 'type': x.value}))
    props = dict(props)
    props.pop('has_coupled_system', None)
    props.pop('label', None)
    return props


def get_class_options(onto, class_label):
    cl = onto.search_one(label = class_label)
    return [x.name for x in cl.subclasses()]


def get_instance_properties(onto, inst_name):
    inst = onto[inst_name]
    props = {}
    for prop in inst.get_properties():
        try:
            props[prop.name] = [x.name for x in prop[inst]]
        except:
            props[prop.name] = prop[inst]
    props.pop('has_coupled_system', None)
    props.pop('label', None)
    return props

    
def get_instance_options(onto, class_label):
    cl = onto.search_one(label = class_label)
    return [x.name for x in cl.instances()]


def add_statement(onto, subj, pred, obj=None):
    pred = onto.search_one(label = pred)
    with onto:
        if not obj:
            cl = get_class(onto, pred.name.replace('has_', ''))
            obj = cl()
        pred[subj].append(obj)
    return obj
