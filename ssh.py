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
        self.client = utils.connectViaSSH(self.username, self.host, self.key, self.password, self.port)
        while True:
            command = typer.prompt(f"{self.username}")
            if command == "exit":
                raise typer.Exit(code=1)
            stdin, stdout, stderr = self.client.exec_command(command)
            out = stdout.read().decode()
            err = stderr.read().decode()
            print(out)
        