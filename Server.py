import yaml

class Server:

    def __init__(self, file_name='servers.yaml', server_dict=None):
        self.file_name = file_name
        self.server_dict = server_dict


    def create_server(self, name, hostname, username, password, role):
        s_dict = {name:{'hostname':hostname,
                        'username': username, 'password': password, 'role': role}}
        self.server_dict +=  s_dict
    """
    update keys and values for server name
    """
    def update_server(name, **kwargs):
        pass

    def delete_server(name):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        with open('my_server.yml', 'w') as yaml_file:
            yaml.dump(self.server_dict, self.file_name, default_flow_style=False)
