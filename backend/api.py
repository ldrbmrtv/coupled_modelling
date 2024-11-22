from flask import *
from main import *


app = Flask(__name__)


@app.route('/api/v1.0/get_instance_properties/', methods=['GET'])
def api_get_instance_properties():
    inst = request.args.get('instance')
    try:
        props = get_instance_properties(inst)
        return jsonify(props), '201'
    except:
        return '400'


@app.route('/api/v1.0/import_coupled_kratos/', methods=['POST'])
def api_import_coupled_kratos():
    args = request.get_json()
    data = args.get('data')
    label = args.get('label')
    try:
        coupled_system = import_coupled_kratos(data, label)
        return jsonify(coupled_system), '201'
    except:
        return '400'


@app.route('/api/v1.0/save_onto/', methods=['POST'])
def api_save_onto():
    try:
        save_onto()
        return '201'
    except:
        return '400'


@app.route('/api/v1.0/create_coupled/', methods=['POST'])
def api_create_coupled():
    args = request.get_json()
    label = args.get('label')
    try:
        inst = create_coupled(label)
        return jsonify(inst), '201'
    except:
        return '400'


@app.route('/api/v1.0/copy_instance/', methods=['POST'])
def api_copy_instance():
    args = request.get_json()
    inst = args.get('instance')
    parent = args.get('parent')
    data = args.get('data')
    try:
        inst = copy_instance(inst, parent, data)
        return jsonify(inst), '201'
    except:
        return '400'


@app.route('/api/v1.0/create_instance/', methods=['POST'])
def api_create_instance():
    args = request.get_json()
    prop = args.get('property')
    parent = args.get('parent')
    data = args.get('data')
    try:
        inst = create_instance(prop, parent, data)
        return jsonify(inst), '201'
    except:
        return '400'


@app.route('/api/v1.0/infer_coupled_structure/', methods=['POST'])
def api_infer_coupled_structure():
    args = request.get_json()
    inst = args.get('coupled_system')
    try:
        infer_coupled_system_structure(inst)
        return '201'
    except:
        return '400'


@app.route('/api/v1.0/export_coupled_kratos/', methods=['POST'])
def api_export_coupled_kratos():
    args = request.get_json()
    inst = args.get('coupled_system')
    try:
        export = export_coupled_kratos(inst)
        return jsonify(export), '201'
    except:
        return '400'


if __name__ == "__main__":
    app.run()
