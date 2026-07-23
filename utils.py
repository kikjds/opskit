import paramiko
import typer
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