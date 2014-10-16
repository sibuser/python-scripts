import sublime
import sublime_plugin
from subprocess import Popen, PIPE, STDOUT
import os

def insert_output(view, edit):
    uncrustify_cfg = os.path.join(os.path.expanduser("~"), '.uncrustify.cfg')

    for region in view.sel():
        if view.substr(region) == '':
            r = sublime.Region(0, view.size())
        else:
            r = region

        try:
            p = Popen(['uncrustify', '-c', uncrustify_cfg, '-l', 'cpp'],
                stdin=PIPE, stdout=PIPE, stderr=PIPE)
            result, err = p.communicate(input=view.substr(r).encode('utf-8'))

            if p.returncode != 0:
                raise Exception('Return code: {0} because {1}'.format(str(p.returncode),
                    err.decode('utf-8').split('\n')[0]))
        finally:
            p.stdin.close()
        view.replace(edit, r, result.decode('utf-8'))

class UncrustifyCommand(sublime_plugin.TextCommand):
    def run(self, edit):
      insert_output(self.view, edit)