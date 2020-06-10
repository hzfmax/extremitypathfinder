import os
import re
import sys
from os.path import abspath, isfile, join, pardir

"""
required packages
numpy
(numba)


these packages have to be installed in virtual environment in use:

right python version! (will influence the tox environments!)
for testing:
conda install pytest
conda install isort
conda install twine

pip install rstcheck pip-tools

rstcheck>=3.3.1
twine for uploading securely

documentation generation:
conda install sphinx
https://docs.readthedocs.io/en/stable/intro/getting-started-with-sphinx.html

Use the Makefile to build the docs, like so:
make html


--cov-config=tox.ini

pip-tools package:
TODO write bash script for this
its important to pin requirements to get reproducible errors!
compile a new requirements file (with the latest versions)

source activate tzEnv
pip-compile --upgrade
same as?!:
pip-compile --output-file requirements_tests.txt requirements_tests.in
only update the flask package:
pip-compile --upgrade-package flask
compile a new requirements file (with versions currently used in the virtual env )
pip-compile --generate-hashes requirements_numba.in

do NOT sync. will install ONLY the packages specified! (tox etc. would not be installed any more!)
pip-sync

commands
tox -r to rebuild your tox virtualenvs when you've made changes to requirements setup
# rstcheck will complain about non referenced hyperlinks in doc .rst files! (cannot detect cross file references!)
rstcheck *.rst
tox -r -e codestyle
tox -r -e py37
tox -r -e py37-numba

automatically update imports: isort -rc .
dont use for playground.py


Use the Makefile to build the docs, like so:
cd ./docs
make html
# for online build of docs, release tag must be created!

use bandit to check for vulnerabilities:

conda install bandit
bandit ./timezonefinder/*.py

"""

PACKAGE = 'extremitypathfinder'
VERSION_FILE = 'VERSION'
VIRT_ENV_NAME = 'pathEnv'
VIRT_ENV_COMMAND = f'. ~/miniconda3/etc/profile.d/conda.sh; conda activate {VIRT_ENV_NAME}; '
# TODO '36',
PY_VERSION_IDS = ['37', '38']  # the supported python versions to create wheels for
PYTHON_TAG = '.'.join([f'py{v}' for v in PY_VERSION_IDS])


def get_version():
    return open(VERSION_FILE, 'r').read().strip()


def parse_version(new_version_input='', old_version_str='1.0.0'):
    new_version_input = re.search(r'\d\.\d\.\d+', new_version_input)

    if new_version_input is None:
        raise ValueError  # will cause new input request
    else:
        new_version_input = new_version_input.group()

    # print(new_version_input)

    split_new_version = [int(x) for x in new_version_input.split('.')]
    # print(split_new_version)
    split_old_version = [int(x) for x in old_version_str.split('.')]
    # print(split_old_version)

    for i in range(3):
        if split_new_version[i] > split_old_version[i]:
            break
        if split_new_version[i] < split_old_version[i]:
            raise ValueError  # will cause new input request

    return new_version_input


def set_version(new_version_str):
    with open(VERSION_FILE, 'w') as version_file:
        version_file.write(new_version_str)


def routine(command=None, message='', option1='next', option2='exit'):
    while 1:
        print(message)

        if command:
            print('running command:', command)
            os.system(command)

        print('__________\nDone. Options:')
        print('1)', option1)
        print('2)', option2)
        print('anything else to repeat this step.')
        try:
            inp = int(input())

            if inp == 1:
                print('==============')
                break
            if inp == 2:
                sys.exit()

        except ValueError:
            pass
        print('================')


if __name__ == "__main__":

    print('Do you want to switch to the "dev" branch? Commit before switching branch!')
    print('1) yes, change now.')
    print('2) no, exit')
    print('anything else skip.')
    try:
        inp = int(input())
        if inp == 1:
            os.system('git checkout dev')
            print('==============')
        if inp == 2:
            sys.exit()
    except ValueError:
        pass

    old_version = get_version()

    print('The actual version number is:', old_version)
    print('Enter new version number:')
    version_input = None
    while 1:
        try:
            version_input = input()
            version_str = parse_version(version_input, old_version)
            set_version(version_str)
            break
        except ValueError:
            print(
                f'Invalid version input. Should be of format "x.x.xxx" and higher than the old version {old_version}.')
            pass  # try again

    version = get_version()
    print('the version number has been set to:', version)
    print('=====================')

    routine(None, 'Remember to properly specify all supported python versions in publish.py and setup.py')
    routine(None, 'Maybe re-pin the test dependencies (requirements.txt) with pip-compile!'
                  ' Commands are written in the beginning of this script')
    routine(None, 'Have all pinned dependencies been listed in setup.py and the Documentation?', )
    routine(None, 'Have all (new) features been documented?')
    routine(None, f'Remember to write a changelog now for version {version}')

    print('___________')
    print('Running TESTS:')

    routine(f'{VIRT_ENV_COMMAND} rstcheck *.rst', 'checking syntax of all .rst files:', 'next: build check')

    print('generating documentation now...')
    os.system('(cd ./docs && exec make html)')
    print('done.')

    # IMPORTANT: -r flag to rebuild tox virtual env
    # only when dependencies have changed!
    rebuild_flag = ''
    print('when the dependencies (in requirements_docs.txt) have changed enter 1 (-> rebuild tox)')
    try:
        inp = int(input())
        if inp == 1:
            rebuild_flag = '-r'
    except ValueError:
        pass

    routine(f'{VIRT_ENV_COMMAND} tox {rebuild_flag} -e codestyle', 'checking syntax, codestyle and imports',
            'run tests')
    routine(f'{VIRT_ENV_COMMAND} tox {rebuild_flag} -e py37', 'run tests')
    print('Tests finished.')

    routine(None,
            'Please commit your changes, push and wait if Travis tests build successfully. '
            'Only then merge them into the master.',
            'CI tests passed & merge into master complete. Build and upload now.')

    print('=================')
    print('PUBLISHING:')

    # routine("python3 setup.py sdist bdist_wheel upload", 'Uploading the package now.') # deprecated
    # new twine publishing routine:
    # https://packaging.python.org/tutorials/packaging-projects/
    # delete the build folder before to get a fresh build
    routine(f"rm -r -f build; python setup.py sdist bdist_wheel --python-tag {PYTHON_TAG}", 'building the package now.',
            'build done. check the included files! test uploading.')

    path = abspath(join(__file__, pardir, 'dist'))
    all_archives_this_version = [f for f in os.listdir(path) if isfile(join(path, f)) and version_str in f]
    paths2archives = [abspath(join(path, f)) for f in all_archives_this_version]
    command = "twine upload --repository-url https://test.pypi.org/legacy/ " + ' '.join(paths2archives)

    # upload all archives of this version
    routine(VIRT_ENV_COMMAND + command, 'testing if upload works.')

    command = f"twine upload " + ' '.join(paths2archives)
    routine(VIRT_ENV_COMMAND + command, 'real upload to PyPI.')

    # tag erstellen
    routine(None, 'Do you want to create a git release tag?', 'Yes', 'No')
    routine(f"git tag -a v{version} -m 'Version {version}'; git push --tags", 'Creating tag')
    print(f'______________\nCongrats! Published version {version}.')
