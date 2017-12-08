#!/usr/bin/python3
import init.programSetup as setup
import sys


def init():
    setup.AppSetup.run_setup()


def main():
    init()
    sys.exit()


main()
