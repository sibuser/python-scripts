#!/usr/bin/env python3
import re
import sys

if len(sys.argv) < 1:
    f = open(sys.argv[1], 'r')
else:
    f = open('test.cc', 'r')
buf = []
intend = 0

def briefDetails(buf, string, amountOfSpaces = 12):
    matcher = re.match(r'(\s\*\s)(\\\w+)(\s*)(.*)', string)
    firstPart = ' * ' + matcher.group(2)
    buf.append(firstPart + ' ' * (amountOfSpaces - len(firstPart)) + matcher.group(4) + '\n')
    global intend
    intend = 10

def restPart(buf, string, amountOfSpaces = 31):
    matcher = re.match(r'(\s\*\s)(\\\w+)(\s*)(\w*)(\s+)(.*)', string)
    firstPart = ' * ' + matcher.group(2) + ' ' + matcher.group(4)
    buf.append(firstPart + ' ' * (amountOfSpaces - len(firstPart)) + matcher.group(6) + '\n')
    global intend
    intend = 29

def param(buf, string, amountOfSpaces = 31):
    matcher = re.match(r'(\s\*\s)(\\\w+)(\s*)(\[.*\])(\s*)(\w*)(\s+)(.*)', string)
    firstPart = ' * ' + matcher.group(2) + ' ' + matcher.group(4) + ' ' + matcher.group(6)
    buf.append( firstPart +
               ' ' * (amountOfSpaces - len(firstPart)) +
               matcher.group(8) + '\n')
    global intend
    intend = 29

def alignment(buf, string):
    matcher = re.match(r'(\s\*)(\s*)(.*)', string)
    buf.append(' *' + ' ' * intend + matcher.group(3) + '\n')

for line in f:
    if '/**' in line:

        # if len(line) is not 4:
        #     tmp = list(line)
        #     buf.append(''.join(tmp[0:3]) + '\n')
        #     buf.append(' * ' + ''.join(tmp[4:]))
        # else:
        buf.append(line)

        for line2 in f:

            if '\\brief' in line2:
                briefDetails(buf,line2)
                continue
            elif '\details' in line2:
                briefDetails(buf,line2)
                continue
            elif '\pre' in line2:
                briefDetails(buf,line2)
                continue
            elif '\\return' in line2:
                restPart(buf,line2)
            elif '\\retval' in line2:
                restPart(buf,line2)
            elif '\exception' in line2:
                restPart(buf,line2)
            elif '\\remark' in line2:
                restPart(buf,line2, 1)
            elif '\param' in line2:
                param(buf,line2)
            elif re.match(r'\s\*\s{3,}', line2):
                alignment(buf,line2)
            else:
                buf.append(line2)
            if "*/" in line2: break
    else:
        buf.append(line)
r = open('result.cc', 'w')

for i in buf:
    r.write(i)

