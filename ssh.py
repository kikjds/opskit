import utils
import typer

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
            typer.echo("Missing host or username")
            raise typer.Exit(code=1)
        
        typer.echo(f"Connecting to {self.host}...")
        self.client = utils.connectViaSSH(self.username, self.host, self.key, self.password, self.port)
        
        if self.client is None:
            typer.echo("Connection failed")
            raise typer.Exit(code=1)
        
        typer.echo(f"Connected as {self.username}@{self.host}")
        typer.echo("Type 'exit' to close session\n")
        
        while True:
            try:
                command = typer.prompt(f"{self.username}@{self.host}")
                
                if command.lower() == "exit" or command.lower() == "quit":
                    typer.echo("Closing session")
                    break
                
                if not command.strip():
                    continue
                
                stdin, stdout, stderr = self.client.exec_command(command)
                out = stdout.read().decode()
                err = stderr.read().decode()
                
                if out:
                    typer.echo(out)
                if err:
                    typer.echo(f"{err}")
                    
            except KeyboardInterrupt:
                typer.echo("\nType 'exit' to close")
                continue
            except Exception as e:
                typer.echo(f"Error: {e}")