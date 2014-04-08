#!/usr/bin/env python
__email__ = 'sibuser.nsk@gmail.com'
__author__ = 'sibuser'

import sys
import os
import commands
import subprocess
from itertools import izip_longest, islice

help_path = os.environ['HOME'] + '/help'
info_message = '\033[1;32mINFO:\033[1;m '
error_message = '\033[1;31mERROR:\033[1;m '

"""
This script is intended to be used a small help system where you can save
all your small notes in different files. Each name is a set of tags divided
by underscore sign like my_first_note.
If there are more then one file then all will be opened in less editor for linux and
default editor in windows.
You can sort out files by giving several tags like 'help my note'.
"""


def install():
    """
    Creates a help folder in your home directory with one file as an example.
    Redefines keys for less program to be able to navigate through opened files
    by arrow keys (lef and right) instead of default (:n and :p).
    """
    if not os.path.isdir(help_path):
        os.mkdir(help_path)
        print(info_message + 'The help folder has been created at \'' +
              help_path + '\'')

    with open(help_path + '/my_first_note', 'w') as f:
        f.write('Congratulations! This is your first note.\n'
                'Now you can use it.\n')
        print(info_message + 'The first note has been created \'my_first_note\'')
    if os.name == 'posix':
        with open(os.environ['HOME'] + '/.lesskey', 'w') as lesskey:
            lesskey.write("""\tx         quit
                X         quit
               \e[C        next-file
               \e[D        prev-file
               \eOC        next-file
               \eOD        prev-file""")

        os.system('lesskey ' + os.environ['HOME'] + '/.lesskey')
        print(info_message + 'Navigation keys for less has been redefined and to navigate')
        print(info_message + 'through files you can use left and right arrows instead of :n and :p')


def update():
    """
    If you have a git repo in your help folder then this function
    will commit all changes as a commit message will be used names of
    changed files
    """
    old_pwd = os.getcwd()
    os.chdir(help_path)
    commands.getoutput('git add -A . | git diff HEAD --name-only | tr \'\n\' \' \' '
                       '| awk \'{cmd = "git commit -m \""$0"\""; system(cmd)}\'\', \'')
    os.chdir(old_pwd)


def columnize(sequence, columns=8):
    """
    Returns a column formated string of items from a list
    """
    size, remainder = divmod(len(sequence), columns)
    if remainder:
        size += 1
    slices = [islice(sequence, pos, pos + size)
              for pos in xrange(0, len(sequence), size)]
    return izip_longest(fillvalue='', *slices)

exclude = ['.git', 'deleted', '~$', '~']


def print_all_tags():
    """
    Returns all tags from the help directory.
    """
    # returns sorted unic tags used in names of files
    all_tags = sorted(set(('_'.join([filename for filename in os.listdir(help_path)
              if all(map(lambda tag: tag not in filename, exclude))])).split('_')))

    for values in columnize(all_tags):
        print ' '.join(value.ljust(20) for value in values)


def find_files():
    """
    Searches all files in the help directory and open them in less.
    Supports several tags at the same time and matches them by word occurrence.
    """
    all_files = os.listdir(help_path)
    all_tags = sys.argv[1:]

    result = [help_path + '/' + filename for filename in all_files
              if all(map(lambda tag: tag in filename, all_tags))
        and all(map(lambda tag: tag not in filename, exclude))]
    if len(result) == 0:
        print(error_message + 'Nothing was found')
    else:
        if os.name == 'posix':
            os.system('less ' + ' '.join(result))
        elif os.name == 'nt':
            [os.system("start " + filename) for filename in result]
        else:
            print error_message + 'The current system is not supported'


if __name__ == '__main__':
    if not os.path.isdir(help_path):
        filename = raw_input('Probably you run this script first time '
                             'do you want to continue?[Y/n]')
        if filename == 'Y' or filename == 'y' or filename == '':
            install()
            sys.exit(0)
        else:
            sys.exit(1)
    if len(sys.argv[1:]) == 0:
        print_all_tags()
    elif '--update' in sys.argv[:]:
        update()
    else:
        find_files()
