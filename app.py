from dotenv import load_dotenv
from github import Github
import os
from config import projects, metrics
from rich.table import Table
from rich.console import Console
import requests

load_dotenv()

console = Console()


class metrics:
    class git:
        def get_stargazer_count(project: str):
            repo = g.get_repo(project)
            return repo.stargazers_count

        def get_fork_count(project: str):
            repo = g.get_repo(project)
            return repo.forks

    class docker:
        def get_pulls(project):
            r = requests.get(f"https://hub.docker.com/v2/repositories/{project}")
            content = r.json()
            pull_count = content["pull_count"]

            return pull_count

    class pypi:
        def create_credentials(env_var="BIG_QUERY_CREDENTIALS"):
            with open("BigQueryCredentials.json", "w") as file:
                file.write(os.environ[env_var])

        def get_downloads(project, credentials):
            import subprocess

            try:
                json_str = subprocess.check_output(
                    ["pypinfo", "-j", "--start-date", "2019-01-01", project]
                )
                import json

                content = json.loads(json_str)
                download_count = content["rows"][0]["download_count"]
                return download_count
            except:
                return 0

    def plus_minus_color(number):
        if number > 0:
            return f"[green]{number:,}[/green]"
        if number < 0:
            return f"[bright red]{number:,}[/bright red]"
        else:
            return f"{number:,}"


g = Github(os.environ["GITHUB_TOKEN"])
pypi_credentials = metrics.pypi.create_credentials()

content = []
for project in projects:
    project["stargazers"] = metrics.git.get_stargazer_count(project["github"])
    project["forks"] = metrics.git.get_fork_count(project["github"])
    project["docker_pulls"] = metrics.docker.get_pulls(project["docker"])
    project["pip_installs"] = metrics.pypi.get_downloads(
        project["pypi"], pypi_credentials
    )
    content.append(project)


table = Table(show_header=True, header_style="bold")
table.add_column("Project")
table.add_column("[yellow]Stars[/yellow] :star:", justify="right")
table.add_column("")
table.add_column("[gray]Forks[/gray] 🍴", justify="right")
table.add_column("")
table.add_column("[blue]Docker[/blue] :whale:", justify="right")
table.add_column("")
table.add_column("[green]Pip[/green] :snake:", justify="right")
table.add_column("")

for project in content:
    if project == content[0]:
        table.add_row(
            project["name"],
            f"{project['stargazers']:,}",
            "",
            f"{project['forks']:,}",
            "",
            f"{project['docker_pulls']:,}",
            "",
            f"{project['pip_installs']:,}",
            "",
            style="bold",
        )
    else:
        table.add_row(
            project["name"],
            f"{project['stargazers']:,}",
            metrics.plus_minus_color(project["stargazers"] - projects[0]["stargazers"]),
            f"{project['forks']:,}",
            metrics.plus_minus_color(project["forks"] - projects[0]["forks"]),
            f"{project['docker_pulls']:,}",
            metrics.plus_minus_color(
                project["docker_pulls"] - projects[0]["docker_pulls"]
            ),
            f"{project['pip_installs']:,}",
            metrics.plus_minus_color(
                project["pip_installs"] - projects[0]["pip_installs"]
            ),
        )

console.print(table)
os.remove("BigQueryCredentials.json")
