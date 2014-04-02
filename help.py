#!/usr/bin/env python

__author__ = 'sibuser'
import sys
import os
import commands

help_path = os.environ['HOME'] + '/help'


def install():
    """
    Creates a help folder in your home directory with one file as an example.
    Redefines keys for less program to be able to navigate through opened files by
    arrow keys (lef and right) instead of default (:n and :p).
    """
    if not os.path.isdir(help_path):
        os.mkdir(help_path)

    with open(help_path + '/my_first_note', 'w') as f:
        f.write('Congratulations! This is your first note.\n'
                'Now you can use it.\n')

    with open(os.environ['HOME'] + '/.lesskey', 'w') as lesskey:
        lesskey.write("""\tx         quit
        X         quit
       \e[C        next-file
       \e[D        prev-file
       \eOC        next-file
       \eOD        prev-file""")
    os.system('lesskey ' + os.environ['HOME'] + '/.lesskey')


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


def get_all_tags():
    """
    Returns all tags from the help directory.
    """
    old_pwd = os.getcwd()
    os.chdir(help_path)
    tags = commands.getoutput('ls | grep -v "install"| grep -v "~" | grep -v "deleted" | grep -v ".git" |'
                              ' tr \'_\' \' \' | tr \' \' \'\n\' | sort -u | column -c 100')
    os.chdir(old_pwd)
    return tags


def find_files():
    """
    Searches all files in the help directory and open them in less.
    Supports several tags at the same time and matches them by word occurrence.
    """
    if len(sys.argv[1:]) == 0:
        print(get_all_tags())
    else:
        files = '-name "*' + sys.argv[1] + '*"'
        for arg in sys.argv[1:]:
            files = files + ' -a -name "*' + arg + '*"'

        result = commands.getoutput('find -L ~/help ' + files + '| grep -v \"~$\" | grep -v \".git/\"'
                                                                '| grep -v \"deleted\"')
        if result == '':
            print('Nothing was found')
        else:
            os.system('less ' + ' '.join(result.strip().split()))


if __name__ == '__main__':
    if not os.path.isdir(help_path):
        filename = raw_input('Probably you run this script first time '
                             'do you want to continue?[Y/n]')
        if filename == 'Yes' or filename == 'yes' or filename == '':
            install()
        else:
            sys.exit(1)
    find_files()

