import argparse
import json
import os
import shutil
import time
import yaml

import rootfs_worker
import iso_worker


ROOTFS_DIR = 'rootfs'
DNF_COMMAND = 'dnf'

parser = argparse.ArgumentParser(description='clone and manipulate git repositories')
parser.add_argument('--package-list', metavar='<package_list>',
                    dest='package_list', required=True,
                    help='Input file including information like package lists and target version.')
parser.add_argument('--config-file', metavar='<config_file>',
                    dest='config_file', required=True,
                    help='Configuration file for the software, including working dir, number of workers etc.')
parser.add_argument('--build-type', metavar='<config_file>',
                    dest='build_type', required=True,
                    help='Specify the build type, should be one of: vhd, livecd-iso, installer-iso')



def parse_package_list(list_file):
    if not list_file:
        raise Exception

    with open(list_file, 'r') as inputs:
        input_dict = json.load(inputs)

    package_list = input_dict["packages"]
    return package_list


def clean_up_dir(target_dir):
    if os.path.exists(target_dir):
        shutil.rmtree(target_dir)


def prepare_workspace(base_dir, parsed_args, config_options):
    work_dir = config_options['working_dir']
    clean_up_dir(work_dir)
    os.makedirs(work_dir)
    packages = parse_package_list(parsed_args.package_list)

    verbose = False
    if config_options.get('debug'):
        verbose = True

    # prepare an empty rootfs folder with repo file in place
    rootfs_dir = config_options['working_dir'] + '/' + ROOTFS_DIR
    rootfs_repo_dir = rootfs_dir + '/etc/yum.repos.d'

    # TODO: make this configurable
    repo_file = base_dir + '/etc/openEuler.repo'

    os.makedirs(rootfs_dir)
    os.makedirs(rootfs_repo_dir)
    shutil.copy(repo_file, rootfs_repo_dir)

    print('Create a clean dir to hold all files required to make iso ...')
    iso_base_dir = work_dir + '/iso'
    clean_up_dir(rootfs_dir)
    os.makedirs(iso_base_dir)

    return rootfs_dir, config_options['working_dir'], iso_base_dir, packages, repo_file, rootfs_repo_dir, verbose


if __name__ == '__main__':
    start_time = time.time()
    # parse config options and args
    parsed_args = parser.parse_args()

    if parsed_args.build_type not in ['vhd', 'livecd-iso', 'installer-iso']:
        print('Unsupported build-type, Stopped ...')
        sys.exit(1)
    else:
        print('Building:', parsed_args.build_type)

    with open(parsed_args.config_file, 'r') as config_file:
        config_options = yaml.load(config_file, Loader=yaml.SafeLoader)

    base_dir = os.getcwd()
    rootfs_dir, work_dir, iso_base, packages, repo_file, rootfs_repo_dir, verbose = prepare_workspace(
        base_dir, parsed_args, config_options)
    rootfs_worker.make_rootfs(
        rootfs_dir, work_dir, packages, base_dir, config_options, repo_file, rootfs_repo_dir, verbose)
    iso_worker.make_iso(iso_base, base_dir)

    print('ISO: openEuler-test.iso generated in:', work_dir)
    end_time = time.time()
    elapsed_time = end_time - start_time
    print('Elapsed time: %s s' % elapsed_time)
