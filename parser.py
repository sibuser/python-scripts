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

        for line2 in src:
            if "\\brief" in line2:
                tagDescr(buf,line2)
            elif "\details" in line2:
                tagDescr(buf,line2)
            elif "\pre" in line2:
                tagDescr(buf,line2)
            elif "\\return" in line2:
                tagArgDescr(buf,line2)
            elif "\\retval" in line2:
                tagArgDescr(buf,line2)
            elif "\exception" in line2:
                tagArgDescr(buf,line2)
            elif "\\remark" in line2:
                tagArgDescr(buf,line2, 1)
            elif "\tagTwoArgDescr" in line2:
                tagTwoArgDescr(buf,line2)
            elif "\code" in line2:
                # add all strings from \code block into buffer as unchanged
                buf.append(line2)
                for i in src:
                    buf.append(i)
                    if "\endcode" in i: break
            elif re.match(r"\s\*\s{3,}[\w]+", line2):
                alignment(buf,line2)
            else:
                buf.append(line2)
            if "*/" in line2: break
    else:
        buf.append(line)
src.close()

if args.i:
    # open source file again for writing data.
    src = open(args.src,"w")
    for line in buf:
        src.write(line)
    src.close()
elif args.dst:
    # if was passed-in a name of destination file.
    # file will be overwritten
    dst = open(args.dst, "w")
    for line in buf:
        dst.write(line)
    dst.close()
else:
    # by default we will print all buffer into standard output
    for line in buf:
        sys.stdout.write(str(line))