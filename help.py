#!/usr/bin/env python

__author__ = 'sibuser'
import sys
import os
import commands

help_path = os.environ['HOME'] + '/tmp/help'


def install():
    if not os.path.isdir(help_path):
        os.mkdir(help_path)

    with open(help_path + '/my_first_file', 'w') as f:
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
    old_pwd = os.getcwd()
    os.chdir(help_path)
    commands.getoutput('git add -A . | git diff HEAD --name-only | tr \'\n\' \' \' '
                       '| awk \'{cmd = "git commit -m \""$0"\""; system(cmd)}\'\', \'')
    os.chdir(old_pwd)


def he():
    if len(sys.argv[1:]) == 0:
        old_pwd = os.getcwd()
        os.chdir(help_path)
        print(commands.getoutput('ls | grep -v "install"| grep -v "~" | grep -v "deleted" | grep -v ".git" |'
                                 ' tr \'_\' \' \' | tr \' \' \'\n\' | sort -u | column -c 100'))
        os.chdir(old_pwd)
        return
    files = '-name "*' + sys.argv[1] + '*"'
    for arg in sys.argv[1:]:
        files = files + ' -a -name "*' + arg + '*"'

    result = commands.getoutput('find -L ~/tmp/help ' + files + '| grep -v \"~$\" | grep -v \".git/\"'
                                                                '| grep -v \"deleted\"')
    if result == '':
        print('Nothing was found')
    else:
        print(result)
        os.system('less ' + result + ' 2> /dev/null')


def main():
    for arg in sys.argv[1:]:
        if arg == '--install':
            install()
            return
    he()

if __name__ == '__main__':
    main()