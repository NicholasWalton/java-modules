
import os
import shutil
from pathlib import Path
from invoke import task
from textwrap import dedent
import re
import json 
from invoke import task
from pathlib import Path 
from contextlib import contextmanager
import requests


@contextmanager
def change_dir(destination):
    prev_dir = Path.cwd()
    os.chdir(destination)
    try:
        yield
    finally:
        os.chdir(prev_dir)


def copy_dir(from_, base):
    parts = from_.name.split('-')
    level = parts[0]
    module = parts[1]
    to = base / level / module

    shutil.copytree(from_, to )

def walk_modules(root):
    for dir_ in Path(root).glob("**/*"):
        if dir_.name.startswith("Module"):
            yield dir_


def find_java_main_files(start_path):
    """
    Walks through the directory tree starting from start_path and yields the Path
    of each Java source file (.java) that contains a main() method.

    Args:
    - start_path (str or Path): The root directory from which to start searching.
    
    Yields:
    - Path objects pointing to Java files with a main() method.
    """
    start_path = Path(start_path)  # Ensure start_path is a Path object
    pattern = re.compile(r'public\s+static\s+void\s+main\s*\(\s*String\s*\[\s*\]\s+\w+\s*\)')  # Regex to match the main method

    # Walk through the directory tree
    for path in start_path.rglob('*.java'):  # rglob method for recursive globbing
        with open(path, 'r', encoding='utf-8') as file:
            if pattern.search(file.read()):  # Check if the file contains a main() method
                rp = str(path).split('/src/', 1)[-1]
                try:
                    package, clazz = rp.rsplit('/', 1)
                    clazz = clazz.replace('.java','')
                    package = package.replace('/','.')
                    fqn = '.'.join(package.split('.')+[clazz])
                    yield path, package, clazz, fqn
                except ValueError:
                    print("ERROR: Can't process class package", path)

def _move_jars_to_root(root):
    """Actually move the jar files into the lib dir"""
    root = Path(root)

    jars = list(Path(root).glob("**/*.jar"))

    if jars:

        (Path(root) / 'lib').mkdir(exist_ok=True)

        for jar in jars:
            jar.rename(root/"lib"/jar.name)

        (Path(root) / 'lib' / 'jars.txt').write_text('\n'.join([e.name for e in jars])+'\n')

def write_classpath(dir_):
    """Write the eclipse classpath file"""

    dir_ = Path(dir_)

    jf = (dir_/"lib"/"jars.txt")

    if not jf.exists():
        return

    # Do we need this?
    container = dedent(f"""
    <classpathentry kind="con" path="org.eclipse.jdt.launching.JRE_CONTAINER/org.eclipse.jdt.internal.debug.ui.launcher.StandardVMType/JavaSE-1.8">
        <attributes>
            <attribute name="module" value="true"/>
        </attributes>
    </classpathentry>
    """).strip()

    jars_s = ''

    for jar in jf.read_text().splitlines():
        jars_s += f'    <classpathentry kind="lib" path="lib/{jar}"/>\n    '

    cp = dedent(f"""
    <?xml version="1.0" encoding="UTF-8"?>
    <classpath>
        <classpathentry kind="src" path="src"/>
        <classpathentry kind="src" path="images"/>
        <classpathentry kind="output" path="bin"/>
    {jars_s}
    </classpath>
    """).strip()

    (dir_/'.classpath').write_text(cp)

def write_settings(dir_):
    """Write the VSCode settings file"""

    sf = (dir_/".vscode"/"settings.json")

    sf.parent.mkdir(exist_ok=True)

    sf_s = dedent(f"""
    {{
        "java.project.sourcePaths": [
            "images",
            "src"
        ],
        "java.project.outputPath": "bin",
        "java.project.referencedLibraries": [
            "lib/**/*.jar"
        ]
    }}
    """).strip()

    sf.write_text(sf_s+'\n')

def write_gitignore(dir_):
    gi_s = dedent(f"""
    *.class
    bin/*
    !bin/.keep
    .DS_Store
                  
    """).strip()

    (dir_/'.gitignore').write_text(gi_s+'\n')


def write_launch(dir_):
    """Write the VSCode launch.json file"""
    configs = []

    for path, package, clazz, fqn  in find_java_main_files(dir_):
            if clazz not in ('LeagueToken',):
                configs.append(
                    {
                        "type": "java",
                        "name": clazz,
                        "request": "launch",
                        "mainClass": fqn
                    }
                )

    configs = list(sorted(configs, key=lambda e: e['name']))

    lc = {
        "version": "0.2.0",
        "configurations": configs
    }

    (dir_/".vscode"/"launch.json").write_text(json.dumps(lc, indent=4))


def make_dirs(dir_):
    dirs = ['lib','src','images', 'bin']
    for d in dirs:
        p  = dir_/d
        if not p.exists():
            p.mkdir()
            (p/".keep").touch()


def copy_devcontainer(dir_):
    """Copy the devcontainer file from the root into the module"""
    source = Path('./.devcontainer')
    dest = dir_/".devcontainer"

    if not source.exists():
        raise FileNotFoundError(source)

    dest.mkdir(exist_ok=True)

    shutil.copytree(source, dest, dirs_exist_ok=True)

def copy_scripts(dir_):

    source = Path('./scripts')
    dest = dir_/"scripts"

    if not source.exists():
        raise FileNotFoundError(source)

    dest.mkdir(exist_ok=True)

    shutil.copytree(source, dest, dirs_exist_ok=True)


def get_lm(dir_=None):
    
    if dir_ is None:
        p = Path('.')
    else:
        p = Path(dir_)

    _, l, m  = str(p.absolute()).rsplit('/',2)

    assert l.startswith("Level")
    assert m.startswith("Module")

    return l, m


def disable_eclipse(dir_):

    if not (p := Path(dir_)/'.eclipse').exists():
        p.mkdir(parents=True)

    for f in ('.settings', '.classpath', '.project'):
        if ( p:=Path(dir_)/f).exists():
            p.rename(Path(dir_)/'.eclipse'/f)

def make_repo_template(dir_=None, owner="League-Java"):
    """
    Turn a GitHub repository into a template.

    Parameters:
    - owner: str. The username of the repository owner.
    - repo: str. The name of the repository.
   
    """

    l, m = get_lm(dir_)

    repo = f"{l}-{m}"

    github_token = os.environ['GITHUB_TOKEN']


    assert github_token is not None

    url = f"https://api.github.com/repos/{owner}/{repo}"
    headers = {
        "Authorization": f"token {github_token}",
        "Accept": "application/vnd.github.v3+json"
    }
    data = {"is_template": True}

    response = requests.patch(url, headers=headers, json=data)

    if response.status_code == 200:
        print(f"The repository '{repo}' has been successfully turned into a template.")
    else:
        print(f"Failed to turn the repository into a template. Status code: {response.status_code}, Response: {response.text}")



@task
def create_repo(ctx, dir):

    org = "League-Java"
    repo = "Level0-Module0"

    with change_dir(dir):

        if not Path('.git').exists():
            print(f"Create local repo {repo}")
            ctx.run("git init")
            ctx.run("git add -A")
            ctx.run("git commit -a -m'Initial commit'")

        print("Create remote repo")
        try:
            ctx.run(f'gh repo create {org}/{repo} --public -s .  || echo "Repo {org}/{repo} maybe already exists" ')
        except Exception as e:
            print("ERROR", type(e), e)

        print("Push")
        ctx.run("git push -f --set-upstream origin master")


@task 
def update_modules(ctx, root):
    """Update all of the module directories with settings files, scripts, etc. """

    for dir_ in walk_modules(root):
        make_dirs(dir_)
        write_classpath(dir_)
        write_settings(dir_)
        write_gitignore(dir_)
        write_launch(dir_)
        copy_devcontainer(dir_)
        copy_scripts(dir_)
        disable_eclipse(dir_)


@task
def mrt(ctx):
    """Upload the module in the current dir to Github"""
    dir_ = Path('.')
    create_repo(ctx, dir_)
    make_repo_template(dir_)


@task
def de(ctx):
    """Upload the module in the current dir to Github"""
    dir_ = Path('.')


