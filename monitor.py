import time
from datetime import datetime
import psutil
import utils
import typer
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

class Monitor:
    def __init__(self, remote: bool = False, yaml: str = None, file: str = None, username: str = None,
                 host: str = None, port: int = None, key: str = None, password: str = None, interval: float = 10):
        self.remote = remote
        self.yaml = yaml
        self.file = file
        self.interval = interval
        self.console = Console()
        if self.remote and not self.yaml:
            self.username = username
            self.host = host
            self.port = port
            self.key = key
            self.password = password
            self.monitor_remote_resources()
        elif self.remote and self.yaml:
            server = utils.read_yaml_file(self.yaml)
            self.username = server.get("User")
            self.host = server.get("HostName")
            self.port = server.get("Port")
            self.key = server.get("IdentityFile")
            self.password = server.get("Password")
            self.monitor_remote_resources()
        else:
            self.monitor_resources()

    # Monitoring of system resources CPU and RAM usage
    def monitor_resources(self):
        while True:
            cpu_percent = psutil.cpu_percent(interval=0.5)
            memory_usage = psutil.virtual_memory().percent
            memory_info = psutil.virtual_memory()
            memory_usage = memory_info.percent
            now = datetime.now()
            load_1min = psutil.getloadavg()[0]
            usage_panel = self._build_usage_panel(
                now=now,
                cpu_percent=cpu_percent,
                memory_usage=memory_usage,
                used_mb=memory_info.used // (1024 ** 2),
                total_mb=memory_info.total // (1024 ** 2),
                load_1min=load_1min,
            )
            if self.file:
                self.save_to_file(
                    self._build_plain_usage_line(
                        now=now,
                        cpu_percent=cpu_percent,
                        memory_usage=memory_usage,
                        used_mb=memory_info.used // (1024 ** 2),
                        total_mb=memory_info.total // (1024 ** 2),
                        load_1min=load_1min,
                    )
                )
            else:
                self.console.clear()
                self.console.print(usage_panel)
            time.sleep(self.interval)

    def save_to_file(self, usage_data):
        with open(self.file, 'a') as f:
            f.write(f"{usage_data}\n")

    def _build_plain_usage_line(self, now, cpu_percent, memory_usage, used_mb, total_mb, load_1min):
        return (
            f"{str(now)} CPU: {cpu_percent:.1f}% | "
            f"RAM: {memory_usage:.1f}% "
            f"({used_mb}/{total_mb} MB) | "
            f"Load: {load_1min:.2f}"
        )

    def _build_usage_panel(self, now, cpu_percent, memory_usage, used_mb, total_mb, load_1min):
        title = Text("OpsKit Monitor", style="bold cyan")
        timestamp = Text(f"{str(now)}", style="dim")
        cpu_style = self._get_metric_style(cpu_percent)
        mem_style = self._get_metric_style(memory_usage)
        load_style = self._get_metric_style(load_1min * 25)

        body = Text()
        body.append("CPU: ", style="bold white")
        body.append(f"{cpu_percent:.1f}%", style=cpu_style)
        body.append("  |  ", style="dim")
        body.append("RAM: ", style="bold white")
        body.append(f"{memory_usage:.1f}%", style=mem_style)
        body.append(f" ({used_mb}/{total_mb} MB)", style="dim")
        body.append("  |  ", style="dim")
        body.append("Load: ", style="bold white")
        body.append(f"{load_1min:.2f}", style=load_style)

        panel_content = Text.assemble(title, "\n", timestamp, "\n", body)
        return Panel.fit(panel_content, border_style="cyan", padding=(1, 2))

    def _get_metric_style(self, value):
        if value >= 80:
            return "bold red"
        if value >= 60:
            return "bold yellow"
        return "bold green"

    # Monitoring of remote system resources via SSH
    def monitor_remote_resources(self):
        self.client = utils.connectViaSSH(username=self.username, ip=self.host, key=self.key, port=self.port, password=self.password)
        prev_stats = self._get_proc_stats_raw()
        time.sleep(0.5)
        
        while True:
            try:
                now = datetime.now()
                curr_stats = self._get_proc_stats_raw()
                cpu_percent = self._calculate_cpu_usage(prev_stats, curr_stats)
                mem_stats = self._get_mem_stats()

                usage_panel = self._build_usage_panel(
                    now=now,
                    cpu_percent=cpu_percent,
                    memory_usage=mem_stats['used_percent'],
                    used_mb=mem_stats['used_mb'],
                    total_mb=mem_stats['total_mb'],
                    load_1min=mem_stats['load_1min'],
                )
                
                if self.file:
                    self.save_to_file(
                        self._build_plain_usage_line(
                            now=now,
                            cpu_percent=cpu_percent,
                            memory_usage=mem_stats['used_percent'],
                            used_mb=mem_stats['used_mb'],
                            total_mb=mem_stats['total_mb'],
                            load_1min=mem_stats['load_1min'],
                        )
                    )
                else:
                    self.console.clear()
                    self.console.print(usage_panel)
                prev_stats = curr_stats
                
            except Exception as e:
                typer.echo(f"Error: {e}")
            
            time.sleep(self.interval)
        
        self.client.close()
    
    def _get_proc_stats_raw(self):
        stdin, stdout, stderr = self.client.exec_command('cat /proc/stat')
        out = stdout.read().decode()
        err = stderr.read().decode()
        if err:
            typer.echo(f"There was an error: {err}")
            return None
        
        lines = out.split('\n')
        cpu_line = lines[0].split()
        user = int(cpu_line[1])
        nice = int(cpu_line[2])
        system = int(cpu_line[3])
        idle = int(cpu_line[4])
        iowait = int(cpu_line[5])
        irq = int(cpu_line[6])
        softirq = int(cpu_line[7])
        steal = int(cpu_line[8])
        
        total = user + nice + system + idle + iowait + irq + softirq + steal
        idle_time = idle + iowait
        
        return {
            'total': total,
            'idle': idle_time,
            'user': user,
            'system': system,
            'nice': nice,
            'iowait': iowait,
            'irq': irq,
            'softirq': softirq,
            'steal': steal
        }
    
    def _calculate_cpu_usage(self, prev, curr):
        if not prev or not curr:
            return 0.0
        
        total_diff = curr['total'] - prev['total']
        idle_diff = curr['idle'] - prev['idle']
        
        if total_diff == 0:
            return 0.0
        
        usage = ((total_diff - idle_diff) / total_diff) * 100
        return usage
    
    def _get_mem_stats(self):
        stdin, stdout, stderr = self.client.exec_command('cat /proc/meminfo')
        out = stdout.read().decode()
        err = stderr.read().decode()
        if err:
            typer.echo(f"There was an error: {err}")
            return {}
        
        meminfo = {}
        for line in out.split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                meminfo[key.strip()] = int(value.strip().split()[0])
        
        total_mb = meminfo.get('MemTotal', 0) / 1024
        available_mb = meminfo.get('MemAvailable', 0) / 1024
        used_mb = total_mb - available_mb
        used_percent = (used_mb / total_mb) * 100 if total_mb > 0 else 0
        load = self._get_load_average()
        
        return {
            'total_mb': total_mb,
            'available_mb': available_mb,
            'used_mb': used_mb,
            'used_percent': used_percent,
            'load_1min': load[0],
            'load_5min': load[1],
            'load_15min': load[2]
        }
    
    def _get_load_average(self):
        stdin, stdout, stderr = self.client.exec_command('cat /proc/loadavg')
        out = stdout.read().decode().strip()
        err = stderr.read().decode()
        if err:
            typer.echo(f"There was an error collecting load average: {err}")
            return (0.0, 0.0, 0.0)
        parts = out.split()
        return (float(parts[0]), float(parts[1]), float(parts[2]))