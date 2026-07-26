import typer
import utils
import time
class Log:
    def __init__(self, type: str, yaml: str = None, username: str = None, host: str = None,
                 port: int = None, key: str = None, password: str = None):
        self.type = type
        self.username = username
        self.host = host
        self.port = port
        self.key = key
        self.password = password
        if self.type not in ["apache", "nginx", "auth", "syslog"]:
            typer.echo(f"Invalid log type: {self.type}. Valid types are: apache, nginx, auth, syslog")
            raise typer.Exit(code=1)
        if yaml:
            server = utils.read_yaml_file(yaml)
            self.username = server.get("User")
            self.host = server.get("HostName")
            self.port = server.get("Port")
            self.key = server.get("IdentityFile")
            self.password = server.get("Password")
        self.client = utils.connectViaSSH(username=self.username, ip=self.host, key=self.key, port=self.port, password=self.password)
        if self.type == "apache":
            self.fetch_apache_logs()
        elif self.type == "nginx":
            self.fetch_nginx_logs()
        elif self.type == "auth":
            self.fetch_auth_logs()
        elif self.type == "syslog":
            self.fetch_syslog_logs()

    def fetch_apache_logs(self):
        typer.echo("Fetching Apache logs")
        stdin, stdout, stderr = self.client.exec_command("tail -n 0 -f /var/log/apache2/access.log /var/log/apache2/error.log", get_pty=True)
        while True:
            line = stdout.readline()
            if not line:
                if stdout.channel.exit_status_ready():
                    break
                time.sleep(0.1)
                continue
            print(line.strip())
        self.client.close()

    def fetch_nginx_logs(self):
        typer.echo("Fetching Nginx logs")
        stdin, stdout, stderr = self.client.exec_command("tail -n 0 -f /var/log/nginx/access.log /var/log/nginx/error.log", get_pty=True)
        while True:
            line = stdout.readline()
            if not line:
                if stdout.channel.exit_status_ready():
                    break
                time.sleep(0.1)
                continue
            print(line.strip())
        self.client.close()

    def fetch_auth_logs(self):
        typer.echo("Fetching authentication logs")
        stdin, stdout, stderr = self.client.exec_command("tail -n 0 -f /var/log/auth.log", get_pty=True)
        while True:
            line = stdout.readline()
            if not line:
                if stdout.channel.exit_status_ready():
                    break
                time.sleep(0.1)
                continue
            print(line.strip())
        self.client.close()

    def fetch_syslog_logs(self):
        typer.echo("Fetching system logs")
        stdin, stdout, stderr = self.client.exec_command("tail -n 0 -f /var/log/syslog", get_pty=True)
        while True:
            line = stdout.readline()
            if not line:
                if stdout.channel.exit_status_ready():
                    break
                time.sleep(0.1)
                continue
            print(line.strip())
        self.client.close()
