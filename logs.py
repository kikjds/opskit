import typer

class Log:
    def __init__(self, auth: bool = False, nginx: bool = False, apache: bool = False):
        self.auth = auth
        self.nginx = nginx
        self.apache = apache
        if self.auth:
            self.fetch_auth_logs()

    def fetch_auth_logs(self):
        typer.echo("Fetching authentication logs")