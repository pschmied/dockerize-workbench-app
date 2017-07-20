#!/usr/bin/env python3
import json, dpath, re, tempfile, subprocess


def get_relpath_from_git(git_url):
    return(re.search('(?<=/).+(?=.git$)', git_url).group(0))

def get_source(git_url, build_dir):
    '''Clone the git repo referenced in the git_url. Returns nothing if
    successful, otherwise raises an error

    '''
    localpath = os.path.join(
        build_dir,
        get_relpath_from_git(git_url)
    )
        
    subprocess.run('git clone {0}'.format(git_url),
                   shell = True,
                   check = True,
                   cwd = build_dir)
    
    assert os.path.exists(localpath), "Failed to clone repository"

    
def write_params(custom_params, appsrc_dir, filename = 'app_config.json'):
    outpath = os.path.join(appsrc_dir, filename)
    with open(outpath, 'w') as outfile:
        json.dump(custom_params, outfile)


def write_shiny_dockerfile(app_src_path):
    shiny_docker_template = '''
    FROM rocker/shiny
    
    WORKDIR /srv/shiny-server
    
    ADD . /srv/shiny-server

    RUN apt update \\
        && apt install -y -t unstable \\
        libssl-dev \\
        && Rscript packrat/init.R --bootstrap-packrat
    '''

    with open(os.path.join(app_src_path, "Dockerfile"), "w") as dockerfile:
        dockerfile.write(shiny_docker_template)

def write_dockerfile(dockertype, app_src_dir):
    if dockertype == "shiny":
        write_shiny_dockerfile(app_src_dir)
    else raise Exception("Unknown docker application type")

    
def build_docker(app_src_dir, appid):
    subprocess.run('docker build -t {0}'.format(app_id),
                   shell = True,
                   check = True,
                   cwd = app_src_dir)
    


def main():
    # Grab the app config. Imagining that the app-workbench would generate
    # this, but reading from file for illustration purposes now.
    with open(
            '/home/peter/github/dockerize-workbench-app/example-config.json'
            # sys.argv[1]
    ) as config_file:
        app_config = json.load(config_file)

    # Extract the app id
    app_id = dpath.util.get(app_config, "id")
    
    # Create a temp directory
    build_dir = tempfile.TemporaryDirectory()

    # Extract the git src URL from config
    git_url = dpath.util.get(app_config, 'appsrc/giturl')

    # Construct the app's source directory path
    app_src_dir = os.path.join(
        build_dir.name,
        get_relpath_from_git(git_url),
        dpath.util.get(app_config, "appsrc/srcsubdir")
    )

    
    
    # Fetch the app's source
    get_source(git_url, build_dir.name)

    # Write custom parameters to src dir
    write_params(dpath.util.get(app_config, "customparams"),
                 app_src_dir)

    # Write our dockerfile
    write_dockerfile(
        dpath.util.get(app_config, "apptype"),
        app_src_dir
    )

    build_docker(app_src_dir, app_id)
