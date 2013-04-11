#!/usr/bin/env python3

import re
import sys
import argparse

parser = argparse.ArgumentParser(description="This tool formats the text from \
                                                the input file and  \
                                                fixes all indentations in Doxygen \
                                                documentation. By default result \
                                                will be printed into output stream")

parser.add_argument("-i", help="overwrites the original file with a new one", action="store_true")
parser.add_argument("src", help="source file")
parser.add_argument("-dst", help="saves result into file")
args = parser.parse_args()

src = open(args.src, "r+")

buf = []

intend = 0
'''
Function searches the string in format:
* \tag + description
* and set the indentation upon multi string description.
'''
def tagDescr(buf, string, amountOfSpaces = 12):
    matcher = re.match(r"(\s\*\s)(\\\w+)(\s*)(.*)", string)
    firstPart = " * " + matcher.group(2)
    buf.append(firstPart + " " * (amountOfSpaces - len(firstPart)) + matcher.group(4) + "\n")
    global intend
    intend = 10
'''
Function searches the string in format:
* \tag + argument + description
* and set the indentation upon multi string description.
'''
def tagArgDescr(buf, string, amountOfSpaces = 31):
    matcher = re.match(r"(\s\*\s)(\\\w+)(\s*)(\w*)(\s+)(.*)", string)
    firstPart = " * " + matcher.group(2) + " " + matcher.group(4)
    if len(firstPart) < 31:
        buf.append(firstPart + " " * (amountOfSpaces - len(firstPart)) + matcher.group(6) + "\n")
    else:
        buf.append(firstPart + "\n *" + ' ' * (amountOfSpaces - 2) +
                    matcher.group(6) + "\n")
    global intend
    intend = 29
'''
Function searches the string in format:
 * \tag [in/out] argument description
* and set the indentation upon multi string description.
'''
def tagTwoArgDescr(buf, string, amountOfSpaces = 31):
    #                 (r"( * )(first word)(all spaces)([in or out])(all spaces)
    #                 (name of argument)(spaces)(last part of string)")
    matcher = re.match(r"(\s\*\s)(\\\w+)(\s*)(\[.*\])(\s*)(\w*)(\s+)(.*)", string)
    firstPart = " * " + matcher.group(2) + " " + matcher.group(4) + " " + matcher.group(6)
    if len(firstPart) > 31:
        buf.append(firstPart + "\n *" + ' ' * (amountOfSpaces - 2) +
                    matcher.group(8) + "\n")
    else:
        buf.append(firstPart + " " * (amountOfSpaces - len(firstPart)) +
                    matcher.group(8) + "\n")
    # else:
    global intend
    intend = 29
'''
Alignments all string of multi string descroption.
'''
def alignment(buf, string):
    matcher = re.match(r"(\s\*)(\s*)(.*)", string)
    buf.append(" *" + " " * intend + matcher.group(3) + "\n")

for line in src:
    if "/**" in line:
        # if first string of comments longer than 4 characters
        # we will split it on two strings.
        if len(line) > 4:
            matcher = re.match(r"(\/\**)(\\\w.*)", line)
            buf.append('/**\n')
            tagDescr(buf, ' * ' + matcher.group(2))
        else:
            buf.append(line)

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

