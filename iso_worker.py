import os
from shutil import copy


def prepare_iso_linux(iso_base_dir, base_dir):
    # copy isolinux files to the corresponding folder
    isolinux_files = ['isolinux.bin', 'isolinux.cfg', 'ldlinux.c32']
    for file in isolinux_files:
        full_file = base_dir + '/etc/isolinux/' + file
        copy(full_file, iso_base_dir)

    # copy linux kernel to the correspoding folder
    kernel_dir = base_dir + '/etc/vmlinuz'
    copy(kernel_dir, iso_base_dir)


def make_iso(iso_base, base_dir):
    prepare_iso_linux(iso_base, base_dir)
    orig_dir = os.getcwd()
    os.chdir(iso_base)
    cmd = 'mkisofs -o ../openEuler-test.iso -b isolinux.bin -c boot.cat -no-emul-boot -boot-load-size 4 -boot-info-table ./'
    os.system(cmd)
    os.chdir(orig_dir)
