#!/usr/bin/env python3

"""
@copyright (c) 2013, Alexey Ulyanov

"""

import re
import sys
import argparse
import difflib


def main():
    parser = argparse.ArgumentParser(description="This tool formats the text \
                                                    from the input file and  \
                                                    fixes all indentations \
                                                    in format of Doxygen \
                                                    documentation. By default \
                                                    result will be printed \
                                                    into output stream")

    parser.add_argument("-i", help="overwrites the original file",
                        action="store_true", default=False)
    parser.add_argument("-p", help="generate a diff patch ",
                        action="store_true", default=False)
    parser.add_argument("src", help="source file")
    parser.add_argument("-dst", help="saves result into file")
    args = parser.parse_args()

    src = open(args.src, "r+")

    buf = []

    indent = 1  # for alignment multi string descriptions

    """
    * Inserts empty string before
    """


    '''
    * Function searches the string in format:
    * \tag + description
    * and set the indentation upon multi string description.
    '''
    def tagDescr(buf, string, amountOfSpaces=12):
        # add one empty string between next tag and last string of description
        nonlocal indent
        indent = 12 # amount spaces between tag and description
        matcher = re.compile(r"""
            (\s\*\s+) # all spaces and asterisks before tag
            (\\\w+)  # tag itself
            (\s+)    # all spaces between tag and description
            (.*)     # description
            """, re.VERBOSE)
        result = matcher.match(string)
        if result:
            firstPart = " * " + result.group(2)

            if len(firstPart) < 13:
                buf.append(firstPart + " " * (amountOfSpaces - len(firstPart)) \
                    + result.group(4) + "\n")
            # if tag and name of argument are longer then 13 char we
            # will add only one space between tag and description.
            else:
                buf.append(firstPart + " " + result.group(4) + "\n")
        # if we can not recognize a string we just add without changes
        else:
            buf.append(string)

    '''
    * Function searches the string in format:
    * \tag + argument + description
    * and set the indentation upon multi string description.
    '''
    def tagArgDescr(buf, string, amountOfSpaces=31):
        if '*\n' not in buf[len(buf) - 1]:
            buf.append(' * \n')
        nonlocal indent
        indent = 31 # for multi strings description

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
                buf.append(firstPart + " " * (amountOfSpaces - len(firstPart)) \
                    + result.group(6) + "\n")
            else:
                buf.append(firstPart + "\n *" + ' ' * (amountOfSpaces - 2) + \
                            result.group(6) + "\n")
        else:
            buf.append(string)

    '''
    Function searches the string in format:
    * \tag [in/out] argument description
    * and set the indentation upon multi string description.
    '''
    def tagTwoArgDescr(buf, string, amountOfSpaces=31):
        if '*\n' not in buf[len(buf) - 1]:
            buf.append(' * \n')
        nonlocal indent
        indent = 31

        matcher = re.compile(r"""
            (\s\*\s) # all spaces and asterisks before tag
            (\\\w+)  # tag
            (\s+)    # spaces between tag and argument
            (
                (\w+)    # name of argument
                (\s+)    # spaces
                (\[.+\])| # might be [any word]
                (\[.+\])  # might be [any word]
                (\s+)    # spaces
                (\w+)    # name of argument
            )
            (\s+)    # all spaces between tag and description
            (.*)     # description
            """, re.VERBOSE)

        result = matcher.match(string)
        if result:
            iin_out = (8, 7)[result.group(8) == None]
            # here we decide which number of group we will use because
            # you can get arguments in different order
            arg_name = (10, 5)[result.group(8) == None]

            firstPart = " * " + result.group(2) + " " + result.group(iin_out) \
            + " " + result.group(arg_name)
            if len(firstPart) > 31:
                buf.append(firstPart + "\n *" + ' ' * (amountOfSpaces - 2) + \
                            result.group(12) + "\n")
            else:
                buf.append(firstPart + " " * (amountOfSpaces - len(firstPart)) \
                    + result.group(12) + "\n")
        else:
            buf.append(string)



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
        else:
            buf.append(string)

            # 0 \tag + description
    tags = (('\\brief', '\\note', '\\attention', '\details', '\pre'),
            # 1 \tag + argument + description
            ('\\return', '\\retval', '\exception', '\\remark'),
            # 2 \tag + [in/out] + argument + description
            ('\\param',),
            # 3 add a unchanged string into buffer
            ('\code',))

    for line in src:
        if "/**" in line:
            # if first string of comments contains anything except /**
            # we will split it on two strings.
            if len(line) > 4:
                matcher = re.compile(r"""
                    ([\s/*]+) # search /** in any variants
                    (\\\w+.*)    # take any symbols when tag is appeared
                    """, re.VERBOSE)
                result = matcher.match(line)
                if result:
                    buf.append('/**\n')
                    tagDescr(buf, ' * ' + result.group(2))
                else:
                    buf.append(line)
            else:
                buf.append(line)

            for line2 in src:
                if any(word in line2 for word in tags[0]):
                    tagDescr(buf, line2)
                elif any(word in line2 for word in tags[1]):
                    tagArgDescr(buf, line2)
                elif any(word in line2 for word in tags[2]):
                    tagTwoArgDescr(buf, line2)
                elif any(word in line2 for word in tags[3]):
                    # add all strings into buffer as unchanged
                    buf.append(line2)
                    for i in src:
                        buf.append(i)
                        if "\endcode" in i:
                            break
                elif re.match("\s+\*\s+\w+", line2):
                    alignment(buf, line2)
                else:
                    buf.append(line2)
                if "*/" in line2:
                    break
        else:
            buf.append(line)
    src.close()

    if args.p:
        source = open(args.src, 'r').readlines()
        diff = difflib.unified_diff(source, buf)
        sys.stdout.writelines(diff)
    elif args.i:
        # open source file again for writing data.
        src = open(args.src, "w")
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
        sys.stdout.writelines(buf)

if __name__ == '__main__':
    main()
