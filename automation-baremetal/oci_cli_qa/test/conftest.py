'''
Created on May 16, 2018
@author: umartine

===============================================================================
                                Change log
===============================================================================

    Date         GUID        Comment
    -----------------------------------------------------------------------
    2018-05-16   umartine    Initial creation
    2018-05-17   umartine    Add module's Path
    2018-05-18   umartine    Move results to a different folder
    2018-12-11   pcamaril    Add condition to distinguish failures from pipeline tests
    2018-12-12   pcamaril    Remove condition to distinguish pipeline failures
    2019-01-04   umartine    Make Test name an optional field

'''

import sys
sys.path.append("/systemtests/automation-baremetal/oci_cli_qa")

import pytest

from oci_cli_qa.lib.logger import LOG

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    # execute all other hooks to obtain the report object
    outcome = yield
    rep = outcome.get_result()

    # we only look at actual failing test calls, not setup/teardown
    if rep.when == "call" and rep.failed:
        test_name = "default"
        if "test_name" in item.funcargs:
            test_name = item.funcargs["test_name"]
        LOG.info("[Error] test failed")
        LOG.info("[TEST] Finishing test '{0}'".format(test_name))
        open("test_results/{0}.dif".format(test_name), 'a').close()
