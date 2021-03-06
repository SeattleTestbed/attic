"""
Test for creating bundles from an existing on the command line
"""

import os
import sys
import subprocess
import bundle_test_helper

TEST_SRC_FN = "testscript.repy"
TEST_BUNDLE_FN = "testresult.bundle.repy"

# Make sure the bundle doesn't exist to test bundle creation
bundle_test_helper.remove_files_from_directory([TEST_BUNDLE_FN])

# Create a bundle
bundle_test_helper.run_program('bundler.py', ['create', TEST_SRC_FN, TEST_BUNDLE_FN])

# Now run the test script!
bundle_test_helper.run_repy_program(TEST_BUNDLE_FN)