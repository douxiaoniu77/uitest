'''
Created on Mar 14, 2018
@author: umartine

===============================================================================
                                     Change log
===============================================================================

    Date         GUID        Comment
    ----------------------------------------------------------------
    2018-03-14   umartine    Initial creation
    2018-03-14   umartine    Display IP Address
    2018-03-15   umartine    Change test config logic
    2018-03-29   umartine    Add ssh test
    2018-11-21   umartine    Add support to fake instance creation

'''

import json
import time
import os

import oci_cli_qa.lib.operations.compute as compute
import oci_cli_qa.lib.configuration as configuration
import oci_cli_qa.lib.operations.vcn as vcn

from oci_cli_qa.lib.logger import LOG
from oci_cli_qa.lib.runner import run_command

# Configuration files
INSTANCE_CONFIGURATION_JSON = "config/job/compute_instance/config.json"
TEST_CONFIGURATION_JSON = "config/job/compute_instance/tests.json"

# Load configuration
instance_cfg = json.load(open(INSTANCE_CONFIGURATION_JSON))
test_cfg = json.load(open(TEST_CONFIGURATION_JSON))
config = configuration.load_configuration()

# Jobs
def create_instance():
    instance = compute.create_instance(config, instance_cfg)
    vnic_attachment = compute.get_vnic_attachment(config, config["tenancy"], instance.id)
    vnic = vcn.get_vnic(config, vnic_attachment.vnic_id)
    ip_address = vnic.public_ip
    LOG.info("Public IP address: '{0}'".format(ip_address))
    LOG.info("Edit permissions for SSH Key")
    os.chmod(instance_cfg["ssh_key"], 0600)
    LOG.info("Wait 10 minutes for ssh test...")
    time.sleep(10 * 60)
    cmd = ["ssh", "-o", "StrictHostKeyChecking no", "-i", 
           instance_cfg["ssh_key"], "opc@{0}".format(ip_address), "ls"]
    run_command(cmd)


# Jobs
def create_instance_fake():
    compute.create_instance(config, instance_cfg, fake_instance = True)
    
def update_instance_tag():
    compute.update_instance_tag(config, config["tenancy"], instance_cfg["display_name"], 
                                defined_tags, freeform_tags)    

def termiante_instance():
    compute.terminate_instante(config, instance_cfg)
    return

# Run jobs
if test_cfg["create_instance"] and not test_cfg["fake_instance"]: create_instance()
if test_cfg["create_instance"] and test_cfg["fake_instance"]: create_instance_fake()
if test_cfg["update_instance"]: update_instance_tag()
if test_cfg["termiante_instance"]: termiante_instance()
