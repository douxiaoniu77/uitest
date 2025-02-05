'''
Created on Mar 6, 2018
@author: umartine

===============================================================================
                                     Change log
===============================================================================

    Date         GUID        Comment
    ----------------------------------------------------------------
    2018-03-06   umartine    Initial creation
    2018-03-07   umartine    Move files into a config directory
    2018-03-09   umartine    Add logging
    2018-03-29   umartine    Add loging
    2018-05-14   umartine    Removing SSL cert for non-R1
    2018-05-24   umartine    Adding permission to SSH key
    2018-08-03   umartine    Adding path to Oracle DB libs 
    2018-11-19   umartine    Adding proxy configuration

'''
import json
import os

from  oci_cli_qa.lib.logger import LOG

REGION_R1 = "r1.oracleiaas.com"
SSL_CERT_PATH = "config/missioncontrol-root-ca.crt"
ACCOUNT_CONFIGURATION_JSON = "config/account_cfg.json"
DEFAULT_SSH_KEY = "config/SSH_KEY"
#os.chmod(DEFAULT_SSH_KEY, 0600)

def load_configuration():
    LOG.info("[START] Load configuration")
    LOG.info("Load Config file '{0}'".format(ACCOUNT_CONFIGURATION_JSON))
    config = json.load(open(ACCOUNT_CONFIGURATION_JSON))
    # Shared libraries path
    os.environ["LD_LIBRARY_PATH"] = "/usr/lib/oracle/12.1/client64/lib"
    # Proxy configuration
    os.environ["https_proxy"] = "www-proxy-hqdc.us.oracle.com:80"
    os.environ["http_proxy"] = "www-proxy-hqdc.us.oracle.com:80"
    # Certificate for R1
    os.environ["REQUESTS_CA_BUNDLE"] = ""
    if config["region"] == REGION_R1:
        LOG.info("Set SSL Cert for R1 '{0}'".format(SSL_CERT_PATH))
        os.environ["REQUESTS_CA_BUNDLE"] = SSL_CERT_PATH
    LOG.info("[END] Load configuration")
    return config
