#!/usr/bin/env python
import argparse
import os
import sys

import django
from django.conf import settings
from django.test.utils import get_runner

TEST_LABEL_HELP = """\
A test label can take one of four forms:
- path.to.test_module.TestCase.test_method
  run a single test method in a test case
- path.to.test_module.TestCase
  run all the test methods in a test case
- path.to.module
  search for and run all tests in the named Python
  package or module
- path/to/directory
  search for and run all tests below the named directory
"""

os.environ['DJANGO_SETTINGS_MODULE'] = 'tests.settings'
django.setup()
parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument('test_labels', metavar='test_label', nargs='*',
                    help=TEST_LABEL_HELP)
parser.add_argument('--failfast', action='store_true',
                    help='stop after the first test failure is detected')
parser.add_argument('-r', '--reverse', action='store_true',
                    help='sort test cases in the opposite execution order')
parser.add_argument('-v', '--verbosity', choices=(0, 1, 2), default=1, type=int,
                    help='the amount of notification and debug information ')
args = parser.parse_args()

TestRunner = get_runner(settings)
test_runner = TestRunner(verbosity=args.verbosity, reverse=args.reverse,
                         failfast=args.failfast)
failures = test_runner.run_tests(args.test_labels)
sys.exit(bool(failures))
