import paramiko
import typer
import yaml
from pathlib import PurePosixPath, PureWindowsPath

def connectViaSSH(username: str, ip: str, key: str, password: str = None, port: int = 22):
    if key is None and password is None:
        typer.echo("Either key or password must be provided for SSH connection.")
        typer.Exit(code=1)
    if key:
        key_path = str(PureWindowsPath(PurePosixPath(key)))
    
    client = paramiko.client.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    if password:
        client.connect(hostname=ip, port=port, username=username, password=password)
    else:
        print(f"Connecting to {ip} as {username} on port {port} using key: {key_path}")
        client.connect(hostname=ip, port=port, username=username, key_filename=key_path)
    return client

def read_yaml_file(path: str):
    with open(path, "r") as file:
        data = yaml.safe_load(file)
        names = [server.get("name") for server in data.get("servers", [])]
        typer.echo(f"Which server do you want to connect to? {names}")
        selected_server = typer.prompt("Enter the server name")
        server = next((s for s in data.get("servers", []) if s.get("name") == selected_server), None)
        if server is None:
            typer.echo(f"Server '{selected_server}' not found in the YAML file.")
            raise typer.Exit(code=1)
    return server