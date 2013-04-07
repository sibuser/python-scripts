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
                matcher = re.match(r'(.*)brief(\s*)(.*)', line2)
                buf.append(' * \\brief   ' + matcher.group(3) + '\n')
                continue
            if 'details' in line2:
                matcher = re.match(r'(.*)details(\s*)(.*)', line2)
                buf.append(' * \\details ' + matcher.group(3) + '\n')
                continue
            if 'details' in line2:
                matcher = re.match(r'(.*)details(\s*)(.*)', line2)
                buf.append(' * \\details ' + matcher.group(3) + '\n')
                continue
            if 'param' in line2:
                matcher = re.match(r'(.*)param(\s*)(\[.*\])(\s*)(\w*)(\s+)(.*)', line2)
                firstPart = ' * \\param ' + matcher.group(3) + matcher.group(4) + matcher.group(5)
                buf.append( firstPart +
                           ' ' * (31 - len(firstPart)) +
                           matcher.group(7) + '\n')
                continue
            else:
                buf.append(line2)
            if "*/" in line2: break
    else:
        buf.append(line)
r = open('result.cc', 'w')

for i in buf:
    r.write(i)

