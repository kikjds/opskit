import paramiko
import typer
import yaml
from pathlib import PurePosixPath, PureWindowsPath
from rich.console import Console
from rich.prompt import Prompt
from rich.table import Table

console = Console()

def connectViaSSH(username: str, ip: str, key: str, password: str = None, port: int = 22):
    if key is None and password is None:
        console.print("[bold red]Either key or password must be provided for SSH connection.[/]")
        raise typer.Exit(code=1)
    if key:
        key_path = str(PureWindowsPath(PurePosixPath(key)))
    
    client = paramiko.client.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    if password:
        client.connect(hostname=ip, port=port, username=username, password=password)
    else:
        console.print(
            f"[yellow]Connecting to[/] {ip} as {username} on port {port} "
            f"using key: [cyan]{key_path}[/]"
        )
        client.connect(hostname=ip, port=port, username=username, key_filename=key_path)
    return client

def read_yaml_file(path: str):
    with open(path, "r") as file:
        data = yaml.safe_load(file)
        names = [server.get("name") for server in data.get("servers", [])]
        table = Table(title="Available servers")
        table.add_column("Name", style="cyan")
        for name in names:
            table.add_row(name)
        console.print(table)
        selected_server = Prompt.ask("Enter the server name")
        server = next((s for s in data.get("servers", []) if s.get("name") == selected_server), None)
        if server is None:
            console.print(f"[bold red]Server '{selected_server}' not found in the YAML file.[/]")
            raise typer.Exit(code=1)
    return server