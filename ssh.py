import utils
import typer
from rich.console import Console
from rich.prompt import Prompt

console = Console()

class SSH:
    def __init__(self, yaml: str = None, username: str = None, host: str = None,
                 port: int = None, key: str = None, password: str = None):
        self.yaml = yaml
        self.username = username
        self.host = host
        self.port = port
        self.key = key
        self.password = password
        self.connect_via_ssh()

    def connect_via_ssh(self):
        if not self.host or not self.username:
            console.print("[bold red]Missing host or username[/]")
            raise typer.Exit(code=1)
        
        console.print(f"[yellow]Connecting to[/] {self.host}...")
        self.client = utils.connectViaSSH(self.username, self.host, self.key, self.password, self.port)
        
        if self.client is None:
            console.print("[bold red]Connection failed[/]")
            raise typer.Exit(code=1)
        
        console.print(f"[bold green]Connected[/] as {self.username}@{self.host}")
        console.print("[dim]Type 'exit' to close session[/]\n")
        
        while True:
            try:
                command = Prompt.ask(f"[cyan]{self.username}@{self.host}[/]")
                
                if command.lower() == "exit" or command.lower() == "quit":
                    console.print("[yellow]Closing session[/]")
                    break
                
                if not command.strip():
                    continue
                
                stdin, stdout, stderr = self.client.exec_command(command)
                out = stdout.read().decode()
                err = stderr.read().decode()
                
                if out:
                    console.print(out, style="white", markup=False)
                if err:
                    console.print(err, style="bold red", markup=False)
                    
            except KeyboardInterrupt:
                console.print("\n[dim]Type 'exit' to close[/]")
                continue
            except Exception as e:
                console.print(f"[bold red]Error:[/] {e}")