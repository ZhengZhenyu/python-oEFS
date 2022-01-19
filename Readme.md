# openEuler From Scratch in Python
A group of python scripts aimed to build bootable openEuler ISO image from a list with packages.

## Usage
Dependencies: 
- rpm packages: `dnf` `mkisofs`
- pypi packages: `pychroot`

Simply run:
```shell
python3 oEFS.py --package-list etc/openEuler-minimal.json --config-file etc/conf.yaml
```

## TODO list
- Boot with calamares installer
- Hierarchical package list support