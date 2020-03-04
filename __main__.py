import os
import sys
import pickle

def load_servers(dir_name):
    servers = []
    if not os.path.exists(dir_name):
        os.mkdir(dir_name)
        return load_servers(dir_name)

    for file in os.listdir(dir_name):
        with open(os.path.join(dir_name,file), 'rb') as f:
            servers.append(pickle.load(f))
    return servers, dir_name

def show_servers(servers):
    server_names = [server["name"] for server in servers]
    for i,server in enumerate(sorted(server_names)):
        print("{:3}. {:15}  ( {}@{} \t-p {:6} via {:<15} )".format(i+1, server, servers[i]['user'], servers[i]['host'], servers[i]['port'], 'none' if servers[i]['via'] == '' else servers[i]['via']))

def get_server_from_input(servers):
    server = input("Enter server id or nickname: ")
    server = find_server(servers, server)
    if server == None:
        print("No such server")
        return
    return server

def show_menu(servers):
    show_servers(servers)
    print("\n")
    print("+. Add server")
    print("-. Delete server")
    print("t. Tunneling port")
    print("c. Change sever settings")
    print("s. Show server parameters")
    print("q. Quit")

def run_option(option, servers, dir_name):
    if option == "+":
        add_server(servers, dir_name)
    elif option == "-":
        delete_server(servers, dir_name)
    elif option == "q":
        quit(0)
    elif option == "t":
        tunnel_port(servers)
    elif option == "s":
        show_server_parameters(servers)
    elif option == "c":
        change_server_settings(servers, dir_name)
    elif option in [server["name"] for server in servers] or option in [str(i+1) for i,_ in enumerate(servers)]:
        run_server(servers, option)

def change_server_settings(servers, dir_name):
    show_servers(servers)
    server = get_server_from_input(servers)
    print("Left parammeter black if you don't want to change it.")
    name = input("New server nickname (old '{}'): ".format(server["name"]))
    if name == "": name = server["name"]
    user = input("New server username (old '{}'): ".format(server["user"]))
    if user == "": user = server["user"]
    host = input("New server hostname (old '{}'): ".format(server["host"]))
    if host == "": host = server["host"]
    port = input("New server port (old '{}'): ".format(server["port"]))
    if port == "": port = server["port"]
    via = input("New server via (old '{}'): ".format(server["via"]))
    if via == "": via = server["via"]
    os.remove(os.path.join(dir_name, server["name"]))
    server["name"] = name
    server["user"] = user
    server["host"] = host
    server["port"] = port
    server["via"]  = via
    with open(os.path.join(dir_name, server["name"]), 'wb') as f:
        pickle.dump(server, f)

def add_server(servers, dir_name):
    new_server = {}
    new_server["name"] = input("Nickname: ")   
    new_server["user"] = input("Username: ")
    new_server["host"] = input("Hostname: ")
    new_server["port"] = input("Port    : ")
    new_server["via"]  = input("Via (server nickname or left blank): ")
    open(os.path.join(dir_name, new_server["name"]), "w+").close()
    with open(os.path.join(dir_name, new_server["name"]), 'wb') as f:
        pickle.dump(new_server, f)
    servers.append(new_server)
    

def find_server(servers, server):
    if server in [s["name"] for s in servers]:
        for s in servers:
            if s["name"] == server:
                return s
    else:
        for i,s in enumerate(servers):
            if server == str(i+1):
                return s
    return None

def show_server_parameters(servers):
    for i, server in enumerate(servers): print("{}. {}".format(i+1, server["name"]))
    server = input("Enter server id or nickname: ")
    server = find_server(servers, server)
    if server == None:
        print("No such server")
        return
    for key in server:
        print(key, ":", server[key])
    input("\nEnter to continue...")

def delete_server(servers, dir_name):
    show_servers(servers)
    server = get_server_from_input(servers)
    if server == None: return
    servers.remove(server)
    os.remove(os.path.join(dir_name, server["name"]))

def add_via_ssh_script(servers, server, exec_str):
    if server["via"] != "":
        via_server = server["via"]
        while True:
            via_server = find_server(servers, via_server)
            exec_str = "ssh -t {}@{} -p {} -o ServerAliveInterval=240 -o ServerAliveCountMax=2 ".format(via_server["user"], via_server["host"], via_server["port"]) + exec_str
            if via_server["via"] != '':
                via_server = via_server["via"]
            else:
                break
    return exec_str

def add_via_and_execute(servers, server, exec_str):
    exec_str = add_via_ssh_script(servers, server, exec_str)
    print("Processing ", exec_str + "...")
    os.system(exec_str)

def run_server(servers, server):
    server = find_server(servers, server)
    if server == None:
        print("No such server")
        return
    exec_str = "ssh {}@{} -p {} -o ServerAliveInterval=240 -o ServerAliveCountMax=2".format(server["user"], server["host"], server["port"])    
    add_via_and_execute(servers, server, exec_str)

def tunnel_port(servers):
    show_servers(servers)
    server     = get_server_from_input(servers)
    here_port  = input("Local port: ")
    there_port = input("Host port: ")
    exec_str   = "ssh -fNL {}:localhost:{} {}@{} -p {}".format(here_port, there_port, server["user"], server["host"], server["port"])
    add_via_and_execute(servers, server, exec_str)

def main():
    SSHARA_DESERT_DIR = ".desert"
    if 'win' in sys.platform:
        user_dir    = os.path.join("C:\\Users",os.getlogin())
        desert_path = os.path.join(user_dir, SSHARA_DESERT_DIR) 
        if not os.path.exists(desert_path): os.mkdir(desert_path)
        SSHARA_DESERT_DIR = desert_path
    else:
        user_dir    = "/usr/share/"
        desert_path = os.path.join(user_dir, SSHARA_DESERT_DIR)
        if not os.path.exists(desert_path): os.mkdir(desert_path)
        SSHARA_DESERT_DIR = desert_path
    while True:
        os.system('cls')
        servers, dir_name = load_servers(SSHARA_DESERT_DIR)
        show_menu(servers)
        try:
            option = input("\n: ")
        except KeyboardInterrupt:
            exit()
        os.system('cls')
        try:
            run_option(option, servers, dir_name)
        except KeyboardInterrupt:
            pass

if __name__=='__main__':
    main()
        
