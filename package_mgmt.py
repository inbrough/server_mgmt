#!/usr/bin/python

import sys
import yaml
import time
import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

""""
    This Class creates SSH connectoin to remote servers, read from yaml file
    servers list, read from file commands.

"""

class Packages:
    report_items = ["hostname", "hostname --ip-address", "iptables -S"]
    report_name = 'package_mgmt.html'
    stdout_output = []
    def __init__(self,hostname, username, password, role, script=None,  retry_time=0):
        self.hostname = hostname
        self.username = username
        self.password = password
        self.role = role
        self.script = script
        self.retry_time = retry_time
        self.__ssh__ = None


        pass
    """
        connect using paramiko using username and password credentials
    """
    def connect(self):
        i = 0
        while True:
            try:
                self.__ssh__ = paramiko.SSHClient()
                self.__ssh__.set_missing_host_key_policy(paramiko.AutoAddPolicy())

                self.__ssh__.connect(hostname=self.hostname, username=self.username, password=self.password)
                break
            except paramiko.AuthenticationException:
                print("Authentication failed when connecting to %s" % self.hostname)
                sys.exit(1)
            except:
                i += 1
                time.sleep(2)
                # If we could not connect within time limit

            if i >= self.retry_time:
                print("Could not connect to %s. Giving up" % self.hostname)
                sys.exit(1)
        # self.print_report()
        return

    """
        optional method to read sets of commands from a file, each command 
        separated by new line
    """
    def read_commands_from_file(self):
        my_file = self.script.readlines()

        for command in my_file:
            stdin, stdout, stderr = self.__ssh__.exec_command(command)
            tmp = stdout.channel.recv(1024)
            output = tmp.decode()
            print output
    """
        print report by a list of sets of commands to be collected 
    """
    def print_report(self, my_stdout=None):
        # stdout_output = []
        with open(self.hostname + '.html', 'w') as f:
            for item in self.report_items:
                stdin, stdout, stderr = self.__ssh__.exec_command(item)
                self.stdout_output.append(stdout.read())

            if my_stdout is not None:
                self.stdout_output.append(my_stdout.read())

            output = '\n'.join(self.stdout_output)
            f.write(output)
            self.stdout_output = []
            f.close()


    def install_packages(self, pkg=None):
        stdin, stdout, stderr = self.__ssh__.exec_command('sudo yum install -y %s' % pkg)
        self.print_report(stdout)
        return

    def update_package(self, pkg=None):
        stdin, stdout, stderr = self.__ssh__.exec_command('sudo yum update ' + pkg)
        self.print_report(stdout)
        return

    def delete_package(self, pkg):
        stdin, stdout, stderr = self.__ssh__.exec_command('sudo yum remove -y %s' % pkg)
        self.print_report(stdout)
        return

    def set_iptables(self, source_port=None, dest_port=None, hostname=None):
        stdin, stdout, stderr = self.__ssh__.exec_command(
            'iptables -A INPUT -p tcp --destination-port {0} -j DROP'.format(dest_port))
        self.print_report(stdout)
        stdin, stdout, stderr = self.__ssh__.exec_command(
            'iptables -A OUTPUT -o eth0 -p tcp --destination-port {0} -s {1} -j DROP'.format(dest_port, hostname))
        self.print_report(stdout)
        return

    def __del__(self):
       print 'Closing connections %s' % self.hostname
       self.__ssh__.close()


def main():

    # reading a yaml file that contains servers connection details
    server_list = yaml.load(open('servers'))

    for server in server_list:
        my_server = server_list[server]['hostname']
        user = server_list[server]['user']
        password = server_list[server]['password']
        role = server_list[server]['role']


        #  on command_list there are some bash commands to be executed
        script = open('command_list', "r")

        # my_test = Packages(my_server, user, password, script, 2)

        my_test = Packages(my_server, user, password, role)
        my_test.connect()
        if role == 'webservers':
            my_test.install_packages('httpd')
            my_test.delete_package('tmux')
            my_test.set_iptables(dest_port=4999, hostname='10.88.55.32')
        elif role == 'db':
            my_test.install_packages('mariadb')
            my_test.install_packages('vim-X11')


if __name__ == "__main__":
    main()
