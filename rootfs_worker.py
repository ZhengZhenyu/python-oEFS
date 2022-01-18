import argparse
import logging
import json
import os
import subprocess
from shutil import copy
import yaml


ROOTFS_DIR = 'rootfs'
DNF_COMMAND = 'dnf'

parser = argparse.ArgumentParser(description='clone and manipulate git repositories')
parser.add_argument('--package-list', metavar='<package_list>',
                    dest='package_list', required=True,
                    help='Input file including information like package lists and target version.')
parser.add_argument('--config-file', metavar='<config_file>',
                    dest='config_file', required=True,
                    help='Configuration file for the software, including working dir, number of workers etc.')
parser.add_argument('--repo-file', metavar='<repo_file>',
                    dest='repo_file', required=True,
                    help='Repository file used in the rootfs.')


def parse_package_list(list_file):
    if not list_file:
        raise Exception

    with open(list_file, 'r') as inputs:
        input_dict = json.load(inputs)

    package_list = input_dict["PackageList"]
    return package_list


if __name__ == '__main__':
    parsed_args = parser.parse_args()
    with open(parsed_args.config_file, 'r') as config_file:
        config_options = yaml.load(config_file, Loader=yaml.SafeLoader)

    if not os.path.exists(config_options['working_dir']):
        os.makedirs(config_options['working_dir'])

    # prepare an empty rootfs folder with repo file in place
    rootfs_dir = config_options + ROOTFS_DIR
    rootfs_repo_dir = rootfs_dir + '/etc/yum.repos.d'
    repo_file = config_options['repo_file']
    os.makedirs(rootfs_dir)
    os.makedirs(rootfs_repo_dir)
    copy(repo_file, rootfs_repo_dir)

    # install filesystem first
    cmd = [DNF_COMMAND, 'install', 'filesystem', '--installroot',
           rootfs_dir, '-y']
    os.system(' '.join(cmd))

    # install the rest of packages from the pkg_list
    pkg_list = parse_package_list(parsed_args.package_list)

    for pkg in pkg_list:
        # filesystem already installed, skip
        if pkg == 'filesystem':
            continue
        else:
            cmd = [DNF_COMMAND, 'install', pkg, '--installroot',
                   rootfs_dir, '-y']
            os.system(' '.join(cmd))

    print('rootfs generated in:\n')
    print(rootfs_dir)
