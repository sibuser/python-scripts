#!/usr/bin/env python

"""
\copyright (c) 2013, Alexey Ulyanov <sibuser.nsk@gmail.com>

"""
# find . -type f -name '*.hh' -exec parser.py -i {} \;

"""
The brief description for a class should give a reason for why it exist and when to use it. What is the class good for. It is important that it can stand for itself.

The details description should give a more thoroughly insight into the use cases for the class.
Provide an example of how to use the class. Add some extra time to this as this code will probably be copy-paste many times.

Specify if the parameter is input [in], output [out] or both [in,out].

The \brief and \details texts should be left aligned at column 13 to get all text aligned, i.e. separate \details from the text with 2 spaces.
The parameter and return description texts should be left aligned at column 32 to get all description texts aligned, i.e. separate \param from the text with 23 spaces. If the parameter, type and variable name extends past column 32 the description should be placed at column 32 on the row below.
Between all parameter or return values an empty line should be added.
Example
/**
 * \brief    Brief description.
 *
 * \details  Details description \ref refernce.
 *
 * \param [in] a_Argunent       Name of input parameter.
 *
 * \param [out] a_Result        Name of output parameter.
 *
 * \param [in,out] a_VeryLongName
 *                              Description.
 *
 * \return                      Description of a return value
 *
 * \code
 *  Some code here.
 * \endcode

 */
Type FunctionName(Type a_Argunent, Type a_Result, Type a_VeryLongName);
"""

import re
import sys
import argparse
import difflib


def main():
    parser = argparse.ArgumentParser(description="""This tool formats the text
                                                    from the input file and
                                                    fixes all indentations
                                                    in format of Doxygen
                                                    documentation. By default
                                                    result will be printed
                                                    into output stream""")

    parser.add_argument("-i", help="overwrites the original file",
                        action="store_true", default=False)
    parser.add_argument("-p", help="generate a diff patch ",
                        action="store_true", default=False)
    parser.add_argument("src", help="source file")
    parser.add_argument("-dst", help="saves result into file")
    args = parser.parse_args()

    src = open(args.src, "r+")
    # multiDescr = False # we need to know where we found a string
    buf = []

    indent = {"i": 1}  # for alignment multi string descriptions
    edge = 0    # alignment from the left edge

    """
    * Inserts empty string before
    """

    def insertLine(buf, string):
        if '*\n' in buf[-1] and '/**' not in buf[-1]:
            buf[-1] = (' ' * edge + '*\n')
        if '/**' and '*\n' not in buf[-1]:
            buf.append(' ' * edge + '*\n')

    '''
    * Function fixes all indentations for strings
    * which don't match to any regExpr.
    '''
    def leftIndent(string, buf):
        matcher = re.compile(r"""
            (\s*\*) # all spaces and asterisks before tag
            (.*)  # tag itself
            """, re.VERBOSE)
        result = matcher.match(string)

        if result:
            buf.append(' ' * edge + "*" + result.group(2) + "\n")
        else:
            buf.append(string)


    '''
    * Function searches the string in format:
    * \tag + description
    * and set the indentation upon multi string description.
    '''
    def tagDescr(buf, string, spaces=13):
        indent["i"] = 12  # amount spaces between tag and description
        insertLine(buf, string)

        matcher = re.compile(r"""
            ([ *]*) # all spaces and asterisks before tag
            ([@\\]+\w+|[.*])  # tag itself
            (\s+)    # all spaces between tag and description
            (.*)     # description
            """, re.VERBOSE)
        result = matcher.match(string)

        if result:
            firstPart = ' ' * edge + "* " + result.group(2)
            if len("* " + result.group(2)) < 13:
                buf.append(firstPart + " " * (spaces - len("* " +
                            result.group(2))) + result.group(4) + "\n")
            # if tag and name of argument are longer then 13 char we
            # will add only one space between tag and description.
            else:
                buf.append(firstPart + " " + result.group(4) + "\n")
        # if we could not recognize a string we just add without changes
        else:
            buf.append(string)
        alignment(buf)

    '''
    * Function searches the string in format:
    * \tag + argument + description
    * and set the indentation upon multi string description.
    '''
    def tagArgDescr(buf, string, spaces=31):
        indent["i"] = 31  # for multi strings description

        insertLine(buf, string)
        matcher = re.compile(r"""
            ([ *]*)  # all spaces and asterisks before tag
            ([@\\]\w+)  # tag itself
            (\s+)       # all spaces
            (\w+)       # name of argument
            (\s+)       # all spaces between argument and description
            (.*)        # description
            """, re.VERBOSE)
        result = matcher.match(string)

        if result:
            tagArg = "* " + result.group(2) + " " + result.group(4)

            if len(tagArg) < spaces:  # spaces between argument and description
                buf.append(' ' * edge + tagArg + " " *
                    (spaces - len(tagArg) + 1) + result.group(6) + "\n")
            else:
                buf.append(' ' * edge + tagArg + "\n" + " " * edge + "*"
                    + ' ' * indent["i"] + result.group(6) + "\n")
        else:
            buf.append(string)
        alignment(buf)

    '''
    Function searches the string in format:
    * \tag [in/out] argument description
    * and set the indentation upon multi string description.
    '''
    def tagTwoArgDescr(buf, string, spaces=32):
        indent["i"] = 31

        insertLine(buf, string)
        matcher = re.compile(r"""
            ([ *]*)    # all spaces and asterisks before tag
            ([@\\]\w+)    # tag
            (\s+)         # spaces between tag and argument
            (
                (\w+)     # name of argument
                (\s+)     # spaces
                (\[[a-z,]+\])| # might be [any word]
                (\[[a-z,]+\])  # might be [any word]
                (\s+)     # spaces
                (\w+)     # name of argument
            )
            (\s+)    # all spaces between tag and description
            (.+)     # description
            """, re.VERBOSE)

        result = matcher.match(string)

        if result:
            # here we decide which number of group we will use because
            # you can get arguments in different order
            in_out = (8, 7)[result.group(8) is None]
            arg_name = (10, 5)[result.group(8) is None]

            tagArg = "* " + result.group(2) + " " + result.group(in_out) \
                    + " " + result.group(arg_name)

            if len(tagArg) < 32:
                buf.append(' ' * edge + tagArg + " " * (spaces - len(tagArg))
                    + result.group(12) + "\n")
            else:
                buf.append(' ' * edge + tagArg + "\n" + (" " * edge) + "*" +
                    (' ' * (spaces - 1)) + result.group(12) + "\n")
        else:
            buf.append(string)

        alignment(buf)

    '''
    Alignments all string of multi string descriptions.
    '''
    def alignment(buf):
        for line in src:
            if any(word in line for word in stopWords):
                leftIndent(line, buf)
                break

            if any(word in line for word in tags):
                [tags[key](buf, line) for key in tags if key in line]
                break

            matcher = re.compile(r"""
                (\s*)      # all spaces before asterisks
                (\*+\s+)    # all spaces and asterisks before description
                (.+)       # description
                """, re.VERBOSE)
            result = matcher.match(line)

            if result:
                buf.append(' ' * edge + "*" + " " * indent["i"] + result.group(3) + "\n")
            else:
                buf.append(line)

            # 0 \tag + description
    tags = {'\\brief'    : tagDescr,
            '\\note'     : tagDescr,
            '\\note'     : tagDescr,
            '\\attention': tagDescr,
            '\\warning'  : tagDescr,
            '\details'   : tagDescr,
            '\pre'       : tagDescr,
            '\defgroup'  : tagDescr,
            '\deprecated': tagDescr,
            '@see'       : tagDescr,
            '\copyright' : tagDescr,
            '\\author'   : tagDescr,
            '\\throw'   : tagDescr,
            '@author'    : tagDescr,
            '\\remark'   : tagDescr,
            # 1 \tag + argument + description
            '\\return'   : tagArgDescr,
            'args['      : tagArgDescr,
            '\\return'   : tagArgDescr,
            '\\retval'   : tagArgDescr,
            '\exception' : tagArgDescr,
            '@return'    : tagArgDescr,
            # 2 \tag + [in/out] + argument + description
            '\\param'    : tagTwoArgDescr,
            '@param'     : tagTwoArgDescr
            }

            # 3 add a unchanged string into buffer
    stopWords = ('\code', '\endcode', '\*', '*/', '*\n')

    for line in src:
        if "/**" in line:
            # if first string of comments contains anything except /**
            # we will split it on two strings.

            # count how many spaces we need to put between left edge and first
            # asterisk
            edge = line.index('*')

            # if len(re.search(r'([\s/*]+)([\\]?\w+.*)', line).group(2)) > 4
            # and '*/' not in line:
            #     matcher = re.compile(r"""
            #         ([\s/*]+)    # search any variants of /**
            #         ([\\]?\w+.*)    # take any symbols when tag is appeared
            #         """, re.VERBOSE)
            #     result = matcher.match(line)
            #     if result:
            #         buf.append((' ' * (edge - 2)) + '/**\n' + \
            #             (' ' * edge) + '* ' + result.group(2))
            #         # tagDescr(buf, '* ' + result.group(2))
            #     else:
            #         buf.append(line)
            # else:
            buf.append(line)

            for line2 in src:
                if "/**" in line2:
                    edge = line2.index('*')

                # for each key in dictionary if key is in a string
                # do call a function
                [tags[key](buf, line2) for key in tags if key in line2]

                if not any(word in line2 for word in tags):
                    leftIndent(line2, buf)
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
