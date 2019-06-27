#!/usr/bin/python3

# Copyright Armijn Hemel for Tjaldur Software Governance Solutions
# SPDX-Identifier: GPL-3.0

# This scripts processes output of ScanCode 3.0.x and ouutputs a file
# with license information and copyright statements per file.
# It requires that ScanCode is invoked with the --full-root option, for
# example:
#
# $ ./scancode --full-root -l -c -e -u --json-pp=/tmp/output.json /path/to/source/directory/
#
# When scanning the Linux kernel it is highly recommended to take advantage of
# the parallel processing options that ScanCode offers. For example, to run with
# eight processes at once:
#
# $ ./scancode --full-root -l -c -e -u -n 8 --json-pp=/tmp/output.json /path/to/source/directory/


import sys
import os
import json
import argparse


def main(argv):
    parser = argparse.ArgumentParser()

    # the following options are provided on the commandline
    parser.add_argument("-j", "--json", action="store", dest="jsonfile",
                        help="path to ScanCode JSON file", metavar="FILE")
    parser.add_argument("-d", "--directory", action="store", dest="toplevel",
                        help="top level directory", metavar="DIR")
    args = parser.parse_args()

    if args.jsonfile is None:
        parser.error("ScanCode JSON file missing")

    if not os.path.exists(args.jsonfile):
        parser.error("ScanCode JSON file does not exist")

    if not os.path.isfile(args.jsonfile):
        parser.error("ScanCode JSON file is not a file")

    if args.toplevel is None:
        parser.error("Top level directory not provided")

    try:
        scjsonfile = open(args.jsonfile).read()
        scjson = json.loads(scjsonfile)
    except:
        print("Cannot parse ScanCode JSON, exiting", file=sys.stderr)
        sys.exit(1)

    pathlen = len(args.toplevel)

    filecounter = 1

    # a set of file names to ignore, should be made configurable (TODO)
    ignore = set(['Makefile', 'Kconfig', 'Kbuild'])

    for f in scjson['files']:
        # skip directories, this needs the source code directory
        # to work correctly
        if os.path.isdir(f['path']):
            continue
        if os.path.basename(f['path']) in ignore:
            continue

        # store results
        sccopyrights = []
        sclicenses = []
        scstatements = set()
        if f['scan_errors'] != []:
            continue
        if f['authors'] != []:
            sccopyrights += f['authors']
        if f['copyrights'] != []:
            for u in f['copyrights']:
                scstatements.add(u['value'])
        if f['licenses'] != []:
            for u in f['licenses']:
                if u['spdx_license_key'] != None:
                    sclicenses.append(u['spdx_license_key'])
                else:
                    sclicenses.append(u['short_name'])
        extraline = False
        print("%d - %s\n" % (filecounter, f['path'][pathlen:]))
        if sclicenses != []:
            licensestring = ", ".join(set(sclicenses))
            print("License(s): %s" % licensestring)
            extraline = True
        if scstatements != set():
            scstatements = list(scstatements)
            if extraline:
                print()
            print("Statement(s): %s" % scstatements[0])
            if len(scstatements) > 1:
                for i in scstatements[1:]:
                    print(i)
            extraline = True
        if extraline:
            print()
        filecounter += 1

if __name__ == "__main__":
    main(sys.argv)
