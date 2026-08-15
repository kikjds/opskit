import typer
from pathlib import Path
from typing import Annotated, Optional
from rich.console import Console

from logs import Log
from monitor import Monitor
from ssh import SSH

console = Console()

app = typer.Typer(
    name="opskit",
    help="Linux administration toolkit"
)

@app.command()
def monitor(
    remote: bool = False,
    yaml: Optional[str] = None,
    file: Optional[str] = None,
    username: Optional[str] = None,
    host: Optional[str] = None,
    key: Annotated[Optional[Path], typer.Option(exists=True)] = None,
    password: Optional[str] = None,
    port: int = 22, 
    interval: float = 10
):
    if key is not None and not key.exists():
        console.print(f"[bold red]Key file {key} does not exist.[/]")
        raise typer.Exit(code=1)
    
    key_str = str(key) if key else None
    
    monitor_instance = Monitor(
        remote=remote, 
        yaml=yaml,
        file=file, 
        username=username, 
        host=host, 
        port=port, 
        key=key_str,
        password=password,
        interval=interval
    )
    
@app.command()
def logs(type: str = typer.Option(prompt="Enter log type (apache, nginx, auth, syslog)"), 
         yaml: Optional[str] = None, username: Optional[str] = None, host: Optional[str] = None,
         port: int = None, key: Optional[str] = None, password: Optional[str] = None):
    
    log_instance = Log(type=type,
                       yaml=yaml,
                       username=username,
                       host=host,
                       port=port,
                       key=key,
                       password=password
    )

@app.command()
def ssh(
    username: Optional[str] = None,
    host: Optional[str] = None,
    key: Annotated[Optional[Path], typer.Option(exists=True)] = None,
    password: Optional[str] = None,
    port: int = 22,
    yaml: Optional[str] = None,
):
      
    if key is not None and not key.exists():
        console.print(f"[bold red]Key file {key} does not exist.[/]")
        raise typer.Exit(code=1)
    key_str = str(key) if key else None

    ssh_instance = SSH( 
            username=username, 
            host=host, 
            port=port, 
            key=key_str,
            password=password,
        )

if __name__ == "__main__":
    app()