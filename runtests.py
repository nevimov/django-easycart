#!/usr/bin/env python
import argparse
import os
import sys

import django
from django.conf import settings
from django.test.utils import get_runner

os.environ['DJANGO_SETTINGS_MODULE'] = 'tests.settings'
django.setup()

HELP_TEST_LABEL = """\
A test label can take one of the four forms:
- path.to.test_module.TestCase.test_method
  run a single test method in a test case
- path.to.test_module.TestCase
  run all test methods in a test case
- path.to.module
  search for and run all tests in the named Python
  package or module
- path/to/directory
  search for and run all tests below the named directory
"""
HELP_FAILFAST = 'stop after the first test failure is detected'
HELP_REVERSE = 'sort test cases in the opposite execution order'
HELP_VERBOSITY = 'the amount of notification and debug information '

parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
add_arg = parser.add_argument
add_arg('test_labels', metavar='test_label', nargs='*', help=HELP_TEST_LABEL)
add_arg('-f', '--failfast', action='store_true', help=HELP_FAILFAST)
add_arg('-r', '--reverse', action='store_true', help=HELP_REVERSE)
add_arg('-v', '--verbosity', choices=(0, 1, 2), default=1, type=int,
        help=HELP_VERBOSITY)
args = parser.parse_args()

TestRunner = get_runner(settings)
test_runner = TestRunner(verbosity=args.verbosity, reverse=args.reverse,
                         failfast=args.failfast)
failures = test_runner.run_tests(args.test_labels)
sys.exit(bool(failures))
