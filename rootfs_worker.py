import os
from shutil import copy

from pychroot import Chroot


RPM_INSTALLER = 'dnf'


def install_rpm(dest_dir, pkg, verbose=False):
    cmd = [RPM_INSTALLER, 'install', pkg, '--installroot',
           dest_dir, '-y']
    if not verbose:
        cmd.append('-q')
    print('Installing:', pkg, '...')
    os.system(' '.join(cmd))


def install_rpms(dest_dir, pkg_list, verbose=False):
    print('Installing RPMs ...')
    # install filesystem first
    install_rpm(dest_dir, 'filesystem', verbose)

    for pkg in pkg_list:
        # filesystem already installed, skip
        if pkg == 'filesystem':
            continue
        else:
            install_rpm(dest_dir, pkg, verbose)

    print('rootfs generated in: ', dest_dir)


def prepare_init_script(source_dir, dest_dir):
    init_file = source_dir + '/etc/init'
    copy(init_file, dest_dir)


def confg_rootfs(dest_dir, config_options):
    with Chroot(dest_dir):
        # TODO: make this configurable
        os.system('echo "root:openEuler" | chpasswd')
        # walk-around to avoid systemd failure
        os.system("sed -i '/SELINUX/{s/enforcing/disabled/}' /etc/selinux/config")
    print('Users and Selinux configuration finished in rootfs.')


def compress_to_gz(dest_dir, work_dir):
    orig_dir = os.getcwd()
    os.chdir(dest_dir)
    # run cpio command to generate rootfs.gz
    os.system('find . | cpio -R root:root -H newc -o | gzip > ../iso/rootfs.gz')
    os.chdir(orig_dir)
    print('Done! rootfs.gz generated at', work_dir + '/iso')


def make_rootfs(dest_dir, work_dir, pkg_list, base_dir, config_options, verbose=False):
    print('Making rootfs ...')
    install_rpms(dest_dir, pkg_list, verbose)
    prepare_init_script(base_dir, dest_dir)
    confg_rootfs(dest_dir, config_options)
    print('Copressing rootfs ...')
    compress_to_gz(dest_dir, work_dir)


