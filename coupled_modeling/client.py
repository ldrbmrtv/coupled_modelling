import requests


class KnowledgeBase:

    def __init__(self, host):
        self.host = host

    def import_coupled_kratos(self, label, data):
        res = requests.post(
            f'{self.host}import_coupled_kratos',
            json={'data': data, 'label': label})
        return res.json()

    def get_instance_properties(self, instance):
        res = requests.get(
            f'{self.host}get_instance_properties',
            params={'instance': instance})
        return res.json()

    def create_coupled(self, label):
        res = requests.post(
            f'{self.host}create_coupled',
            json={'label': 'Onera_FSI'})
        return res.json()

    def create_instance(self, property, parent, data):
        params = {'property': property, 'parent': parent, 'data': data}
        res = requests.post(f'{self.host}create_instance', json=params)
        return res.json()

    def copy_instance(self, instance, parent, data):
        params = {'instance': instance, 'parent': parent, 'data': data}
        res = requests.post(f'{self.host}copy_instance', json=params)
        return res.json()

    def infer_coupled_structure(self, coupled_system):
        res = requests.post(
            f'{self.host}infer_coupled_structure',
            json={'coupled_system': coupled_system})
        return res.json()

    def save(self):
        res = requests.post(f'{self.host}save_onto')
        return res.json()

    def export_coupled_kratos(self, coupled_system):
        res = requests.post(
            f'{self.host}export_coupled_kratos',
            json={'coupled_system': coupled_system})
        return res.json()
