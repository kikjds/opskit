import typer
from pathlib import Path
from typing import Annotated, Optional

from monitor import Monitor

app = typer.Typer(
    name="opskit",
    help="Linux administration toolkit"
)

@app.command()
def monitor(
    remote: bool = False, 
    file: Optional[str] = None,
    username: Optional[str] = None,
    host: Optional[str] = None,
    key: Annotated[Optional[Path], typer.Option(exists=True)] = None,
    password: Optional[str] = None,
    port: int = 22, 
    interval: float = 10
):
    if key is not None and not key.exists():
        typer.echo(f"Key file {key} does not exist.")
        raise typer.Exit(code=1)
    
    key_str = str(key) if key else None
    
    monitor_instance = Monitor(
        remote=remote, 
        file=file, 
        username=username, 
        host=host, 
        port=port, 
        key=key_str,
        password=password,
        interval=interval
    )
    
@app.command()
def logs():
    typer.echo("Fetching system logs")

@app.command()
def ssh():
    typer.echo("Establishing SSH connection")

@app.command()
def cleanup():
    typer.echo("Cleaning up")

if __name__ == "__main__":
    app()