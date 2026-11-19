# Development Environment

## Host Environment

- Operating system: Windows 11 Pro
- Virtualization: WSL2
- Linux distribution: Ubuntu 24.04 LTS
- Container runtime: Docker Desktop
- IDE: Visual Studio Code with WSL integration

## Installed Tools

| Tool | Version |
| --- | --- |
| Git | 2.43.0 |
| Python | 3.12.3 |
| pip | 24.0 |
| jq | 1.7 |
| GNU Make | 4.3 |
| ShellCheck | 0.9.0 |
| Docker Engine | 29.8.2 |
| Docker Compose | 5.5.1 |
| VS Code | 1.141.0 |

## Environment Design

- Application source code is stored in the Linux filesystem.
- Docker Desktop provides the container engine.
- Docker CLI communicates with Docker Desktop through WSL integration.
- GitHub authentication uses an ED25519 SSH key.
- Python project dependencies will use isolated virtual environments.
- Credentials and local configuration files must not be committed.
- Infrastructure components will be installed as required.

## Validation Commands

    git --version
    python3 --version
    pip3 --version
    docker version
    docker compose version
    docker run --rm hello-world
    ssh -T git@github.com

## Environment Status

Docker container execution and GitHub SSH authentication
have been successfully validated.
