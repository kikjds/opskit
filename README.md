# OpsKit

Linux administration toolkit written in Python.

## Features

- System monitoring
- SSH automation
- Log analysis

## Installation

pip install -r requirements.txt

## Usage

python opskit.py --help

## YAML file structure

```yml
servers:
  - name: "Server 1"
    HostName: xyz
    User: root
    IdentityFile: path_to_your_key
  
  - name: "Server 2"
    HostName: xyz
    User: root
    Port: 1410
    Password: your_password
```

## Example usage

```bash
python opskit.py monitor --remote --host 0.0.0.0 --username admin --password strong_password --file file_name.txt --interval 1
```