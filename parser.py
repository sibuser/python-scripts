#!/usr/bin/env python3
import re

f = open('test.cc', 'r')
buf = []

def parseString():
    print('dfg')

for line in f:
    if '/**' in line:
        # if len(line) is not 4:
        #     tmp = list(line)
        #     buf.append(''.join(tmp[0:3]) + '\n')
        #     buf.append(' * ' + ''.join(tmp[4:]))
        # else:
        buf.append(line)

        for line2 in f:
            if 'brief' in line2:
                startString = ' * \\brief   '
                endString = re.match(r'(.*)brief(\s*)(.*)', line2)
                buf.append(startString + endString.group(3) + '\n')
                continue
            if 'details' in line2:
                startString = ' * \\details '
                endString = re.match(r'(.*)details(\s*)(.*)', line2)
                buf.append(startString + endString.group(3) + '\n')
                continue
            if 'details' in line2:
                startString = ' * \\details '
                endString = re.match(r'(.*)details(\s*)(.*)', line2)
                buf.append(startString + endString.group(3) + '\n')
                continue
            else:
                buf.append(line2)
            if "*/" in line2: break
    else:
        buf.append(line)
r = open('result.cc', 'w')

for i in buf:
    r.write(i)

