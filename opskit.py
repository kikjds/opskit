import typer

app = typer.Typer(
    name="opskit",
    help="Linux administration toolkit"
)

@app.command()
def monitor():
    typer.echo("Monitoring system resources")

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