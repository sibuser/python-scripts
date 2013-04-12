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

intend = 0 #for alignment multi string descriptions

'''
Function searches the string in format:
* \tag + description
* and set the indentation upon multi string description.
'''
def tagDescr(buf, string, amountOfSpaces = 12):
    # add one empty string between next tag and last string of description
    if '*\n' not in buf[len(buf) - 1]:
        buf.append(' * \n')

    matcher = re.compile(r"""
        (\s\*\s) # all spaces and asterisks before tag
        (\\\w+)  # tag itself
        (\s+)    # all spaces between tag and description
        (.*)     # description
        """, re.VERBOSE)
    result = matcher.match(string)
    if result:
        firstPart = " * " + result.group(2)

        if len(firstPart) < 13:
            buf.append(firstPart + " " * (amountOfSpaces - len(firstPart)) + result.group(4) + "\n")
        # if tag and name of argument are longer then 13 char we will add only one
        # space between tag and description.
        else:
            buf.append(firstPart + " " + result.group(4) + "\n")

    global intend
    intend = 10

'''
Function searches the string in format:
* \tag + argument + description
* and set the indentation upon multi string description.
'''
def tagArgDescr(buf, string, amountOfSpaces = 31):
    if '*\n' not in buf[len(buf) - 1]:
        buf.append(' * \n')

    matcher = re.compile(r"""
        (\s\*\s)    # all spaces and asterisks before tag
        (\\\w+)     # tag itself
        (\s+)       # all spaces
        (\w+)       # name of argument
        (\s+)       # all spaces between tag and description
        (.*)        # description
        """, re.VERBOSE)
    result = matcher.match(string)
    if result:
        firstPart = " * " + result.group(2) + " " + result.group(4)
        if len(firstPart) < 31:
            buf.append(firstPart + " " * (amountOfSpaces - len(firstPart)) + result.group(6) + "\n")
        else:
            buf.append(firstPart + "\n *" + ' ' * (amountOfSpaces - 2) +
                        result.group(6) + "\n")
    global intend
    intend = 29
'''
Function searches the string in format:
* \tag [in/out] argument description
* and set the indentation upon multi string description.
'''
def tagTwoArgDescr(buf, string, amountOfSpaces = 31):
    if '*\n' not in buf[len(buf) - 1]:
        buf.append(' * \n')

    matcher = re.compile(r"""
        (\s\*\s) # all spaces and asterisks before tag
        (\\\w+)
        (\s+)
        (
            (\w+)    # name of argument
            (\s+)
            (\[.+\])|
            (\[.+\])
            (\s+)
            (\w+)
        )
        (\s+)    # all spaces between tag and description
        (.*)     # description
        """, re.VERBOSE)

    result = matcher.match(string)
    if result:
        IN_OUT   = (8,7)[result.group(8) == None]
        ARG_NAME = (10,5)[result.group(8) == None]

        firstPart = " * " + result.group(2) + " " + result.group(IN_OUT) + " " + result.group(ARG_NAME)
        if len(firstPart) > 31:
            buf.append(firstPart + "\n *" + ' ' * (amountOfSpaces - 2) +
                        result.group(12) + "\n")
        else:
            buf.append(firstPart + " " * (amountOfSpaces - len(firstPart)) +
                        result.group(12) + "\n")
    global intend
    intend = 29
'''
Alignments all string of multi string descriptions.
'''
def alignment(buf, string):
    matcher = re.compile(r"""
        (\s+\*\s+)    # all spaces and asterisks before description
        (.+)          # description
        """, re.VERBOSE)
    result = matcher.match(string)

    if result:
        buf.append(" *" + " " * intend + result.group(2) + "\n")

for line in src:
    if "/**" in line:
        # if first string of comments contains anything except /**
        # we will split it on two strings.
        if len(line) > 4:
            matcher = re.compile(r"""
                (\s*/\*+\s+) # search /** in any variants
                (\\\w+.*)    # take any symbols when tag is appeared
                """,re.VERBOSE)
            result = matcher.match(line)
            if result:
                buf.append('/**\n')
                tagDescr(buf, ' * ' + result.group(2))
        else:
            buf.append(line)


        for line2 in src:
            if "\\brief" in line2:
                tagDescr(buf,line2)
            elif "\\attention" in line2:
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
            elif "\\param" in line2:
                tagTwoArgDescr(buf,line2)
            elif "\code" in line2:
                # add all strings from \code block into buffer as unchanged
                buf.append(line2)
                for i in src:
                    buf.append(i)
                    if "\endcode" in i: break
            elif re.match(r"\s\*\s+[\w]+", line2):
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