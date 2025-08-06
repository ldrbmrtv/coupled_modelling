import requests


class KnowledgeBase:
    """
    An interface to the knowledge base for accessing and manipulating classes, instances and properties of coupled systems.

    Args:
        host (str): URI of the knowledge base.
    """

    def __init__(self, host):
        self.host = host
        
    def import_coupled_kratos(self, label, data):
        """
        Creates an instance of the the coupled system with the given data and label.

        Args:
            label (str): Name for the imported model.
            data (dict): Structured data describing the model.

        Returns:
            The created instance.
        """
        res = requests.post(
            f'{self.host}import_coupled_kratos',
            json={'data': data, 'label': label})
        if res.status_code == 201:
            new_inst = CoupledSystem(self.host, res.json())
            return new_inst
        else:
            return res.json()

    def create_coupled(self, label):
        """
        Creates a new instance of a coupled system with the given label.

        Args:
            label (str): Name of the coupled system.

        Returns:
            The created instance.
        """
        res = requests.post(
            f'{self.host}create_coupled',
            json={'label': label})
        if res.status_code == 201:
            new_inst = CoupledSystem(self.host, res.json())
            return new_inst
        else:
            return res.json()

    def create_instance(self, property, parent, data):
        """
        Creates a new instance under a given parent with the specified property and data.

        Args:
            property (str): Property used to relate the instance.
            parent (str): Parent instance.
            data (dict): Data representing the new instance.

        Returns:
            The created instance.
        """
        params = {'property': property, 'parent': parent.name, 'data': data}
        res = requests.post(f'{self.host}create_instance', json=params)
        if res.status_code == 201:
            new_inst = Instance(self.host, res.json())
            return new_inst
        else:
            return res.json()

    def get_instance(self, name):
        """
        Initializes an instance with the specified name.

        Args:
            name (str): Name of the instance.
        
        Returns:
            The initialized instance.
        """
        inst = Instance(self.host, name)
        return inst

    def save(self):
        """
        Updates the knowledge base on the server.
        """
        res = requests.post(f'{self.host}save_onto')
        return res.json()
    
    def save_locally(self, path):
        """
        Downloads and saves the ontology file locally to the specified path.

        Args:
            path (str): File path to save the ontology to.
        """
        res = requests.get(f'{self.host}save_locally')
        onto_file = res.content
        with open(path, 'wb') as f:
            f.write(onto_file)
        #return res.json()

class Instance:
    """
    Any named individual of the knowledge base.

    Args:
        name (str): Name of the instance.
        host (str): URL of the knowledge base.
    
    Attributess:
        properties (dict): A dictionary of the instance properties.
    """

    def __init__(self, host, name):
        self.name = name
        self.host = host
        self.properties = {}

    def get_properties(self):
        """
        Retrieves properties of the instance.

        Returns:
            Dictionary of properties for the instance.
        """
        res = requests.get(
            f'{self.host}get_instance_properties',
            params={'instance': self.name})
        if res.status_code == 201:
            self.properties = res.json()
        return res.json()

    def make_copy(self, parent, data):
        """
        Duplicates the instance and attaches a newly created duplicate to the specified parent with additional data.

        Args:
            parent (str): The new parent for the copied instance.
            data (dict): Data to update the copied instance.
        
        Returns:
            The created instance.
        """
        params = {'instance': self.name, 'parent': parent.name, 'data': data}
        res = requests.post(f'{self.host}copy_instance', json=params)
        if res.status_code == 201:
            new_inst = Instance(self.host, res.json())
            return new_inst
        else:
            return res.json()
    
class CoupledSystem(Instance):

    def infer_classes(self):
        """
        Generates classes reflecting the structure of the coupled system.
        """
        res = requests.post(
            f'{self.host}infer_coupled_structure',
            json={'coupled_system': self.name})
        return res.json()

    def export_kratos(self):
        """
        Exports the coupled system into a Kratos-compatible format.

        Returns:
            Exported representation as a JSON object.
        """
        res = requests.post(
            f'{self.host}export_coupled_kratos',
            json={'coupled_system': self.name})
        return res.json()
    