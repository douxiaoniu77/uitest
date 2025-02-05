'''
Created on Mar 6, 2018
@author: umartine

===============================================================================
                                     Change log
===============================================================================

    Date         GUID        Comment
    -----------------------------------------------------------------------
    2018-03-06   umartine    Initial creation
    2018-03-12   umartine    Add routine to check if PAAS compartment exists
    2018-03-13   umartine    Add loggin
    2018-04-02   umartine    Add AD List
    2018-04-26   umartine    Add PSMtest policies for ashburn - SITE I support
    2018-04-30   umartine    Stop skipping policy creation
    2018-11-30   umartine    Add parent compartment parameter to create compartment
    2018-12-03   umartine    Add delete compartment function
    2018-12-13   umartine    Add SMTP credential operations
    2019-01-03   ttazhang    Add group operations
    2019-01-03   qxionng     Add user and api operations
    2019-01-03   umartine    Add features to add user to group
    2019-01-04   qxionng     Add tagging features
    2019-01-04   umartine    Fix on upload Key operation
    2019-01-08   umartine    Adding one minute delay to the compartment creation

'''

import time
import oci

from oci_cli_qa.lib.logger import LOG

SPMT_CREDENTIAL_DESCRIPTION="smtp credential username and password for automation"
AD_LIST = ["AD-1", "AD-2"]
REGION_PSM_MAPPING = {"r1.oracleiaas.com": "PSM",
                      "us-ashburn-1": "PSMtest"}


def get_identity_client(config):
    LOG.info("Get Identity Client")
    return oci.identity.identity_client.IdentityClient(config)


def create_smtp_credentials(config):
    LOG.info("[START] Create SMTP Credentials for '{0}'".format(config["user"]))
    smtp_credential= oci.identity.models.CreateSmtpCredentialDetails(
        description = SPMT_CREDENTIAL_DESCRIPTION
        )
    identity_client = get_identity_client(config)
    smtp_response = identity_client.create_smtp_credential(smtp_credential,
                                                           user_id = config["user"]
                                                           ).data
    LOG.info(smtp_response)
    LOG.info("[END] Create SMTP Credentials")
    return smtp_response


def delete_smtp_credentials(config, smtp_credential_id):
    LOG.info("[START] Create SMTP Credentials for '{0}'".format(config["user"]))
    LOG.info("Credential id '{0}'".format(smtp_credential_id))
    identity_client = get_identity_client(config)
    identity_client.delete_smtp_credential(user_id = config["user"],
                                           smtp_credential_id = smtp_credential_id)
    LOG.info("[END] Delete SMTP Credentials")


def create_compartment(config, compartment_name, desc = "Generic description", parent_compartment = None):
    LOG.info("[START] Create Compartment '{0}'".format(compartment_name))
    LOG.info("Description: '{0}'".format(desc))
    LOG.info("Parent Compartment: '{0}'")
    if parent_compartment == None:
        parent_compartment = config["tenancy"]
        LOG.info("Parent Compartment is None, using tenancy ocid: '{0}'".format(parent_compartment))
    identity_client = get_identity_client(config)
    compartment_details = oci.identity.models.CreateCompartmentDetails(
        compartment_id = parent_compartment,
        name = compartment_name,
        description = desc
        )
    identity_response = identity_client.create_compartment(compartment_details)
    compartment = identity_response.data
    LOG.info(compartment)
    LOG.info("Waiting 1 minute to finish Compartment provisioning")
    time.sleep(60)
    LOG.info("[END] Create Compartment")
    return compartment


def get_compartment(config, compartment_name, compartment_id = None):
    LOG.info("[START] Get Compartment '{0}'".format(compartment_name))
    identity_client = get_identity_client(config)
    if compartment_id == None:
        compartment_id = config["tenancy"]
    compartments_response = identity_client.list_compartments(compartment_id)
    compartments = compartments_response.data
    compartment = None
    for compartment_aux in compartments:
        if compartment_aux.name == compartment_name:
            LOG.info("Compartment found:")
            LOG.info(compartment_aux)
            compartment = compartment_aux
            break
    LOG.info("[END] Get Compartment")
    return compartment


def delete_compartment(config, compartment_name, compartment_id = None):
    LOG.info("[START] Delete Compartment '{0}'".format(compartment_name))
    identity_client = get_identity_client(config)
    compartment = get_compartment(config, compartment_name, compartment_id)
    compartment = identity_client.delete_compartment(compartment.id)
    LOG.info("Response: '{0}'".format(compartment.status))
    LOG.info("[END] Delete Compartment")


def get_policy(config, policy_name):
    LOG.info("[START] Get Policy '{0}'".format(policy_name))
    identity_client = get_identity_client(config)
    policies_response = identity_client.list_policies(config["tenancy"])
    policies = policies_response.data
    policy = None
    for policy_aux in policies:
        if policy_aux.name == policy_name:
            LOG.info("Policy found:")
            LOG.info(policy_aux)
            policy = policy_aux
            break
    LOG.info("[END] Get Policy")
    return policy


def get_availability_domain(config, ad_suffix = "AD"):
    LOG.info("[START] Get Availability Domain '{0}'".format(ad_suffix))
    identity_client = get_identity_client(config)
    ad_response = identity_client.list_availability_domains(config["tenancy"])
    ads = ad_response.data
    ad = None
    for ad_aux in ads:
        if ad_suffix in ad_aux.name:
            LOG.info("Availability domain found: '{0}'".format(ad_aux))
            ad = ad_aux
            break
    LOG.info("[END] Get Availability Domain")
    return ad


def create_policy(config, compartment_id, name, statements, desc="Generic description"):
    LOG.info("[START] Create Policy '{0}'".format(name))
    LOG.info("Compartment ID: '{0}'".format(compartment_id))
    LOG.info("Statements: '{0}'".format(len(statements)))
    LOG.info("Description: '{0}'".format(desc))
    identity_client = get_identity_client(config)
    policy_details = oci.identity.models.CreatePolicyDetails(
        compartment_id = compartment_id,
        name = name,
        description = desc,
        statements = statements
        )
    identity_response = identity_client.create_policy(policy_details)
    policy = identity_response.data
    LOG.info(policy)
    LOG.info("[END] Create Policy")
    return policy


def config_psm_compartment(config, paas_compartment_name="paas_compartment"):
    LOG.info("[START] Create PSM Compartment and Policy '{0}'".format(paas_compartment_name))

    # Create PaaS compartment
    LOG.info("Check if compartment exist")
    paas_compartment = get_compartment(config, paas_compartment_name)
    if paas_compartment:
        LOG.info("Compartment already exist: '{0}'".format(paas_compartment.id))
    else:
        paas_compartment = create_compartment(config, paas_compartment_name, "PaaS Compartment")

    # Create PaaS compartment
    LOG.info("Check if policy exist")
    paas_policy = get_policy(config, "paas_policy")
    if paas_policy:
        LOG.info("Policy already exist: '{0}'".format(paas_policy.id))
    else:
        # Create statements for the policy
        LOG.info("Create policies")
        psm_sn = REGION_PSM_MAPPING[config["region"]]
        state_temp = "Allow service {2} to {0} in compartment {1}"
        statements = []
        statements.append(state_temp.format("inspect vcns", paas_compartment.name, psm_sn))
        statements.append(state_temp.format("use subnets", paas_compartment.name, psm_sn))
        statements.append(state_temp.format("use vnics", paas_compartment.name, psm_sn))
        statements.append(state_temp.format("manage security-lists", paas_compartment.name, psm_sn))
        # Create policy in Root compartment
        create_policy(config, config["tenancy"], "paas_policy", statements)

    # Finish routine
    LOG.info("[END] Create PSM Compartment and Policy")
    return paas_compartment.id


def create_group(config, group_name , desc):
    LOG.info("[START] Create Group '{0}'".format(group_name))
    identity_client = get_identity_client(config)
    group_details = oci.identity.models.CreateGroupDetails(
        compartment_id=config["tenancy"],
        name=group_name,
        description=desc
    )
    identity_response = identity_client.create_group(group_details)
    group = identity_response

    LOG.info(group)
    LOG.info("Status : '{0}'".format(group.status))
    LOG.info("[END] Create Group")
    return group


def get_group(config, group_name, compartment_id = None):
    LOG.info("[START] Get Group '{0}'".format(group_name))
    identity_client = get_identity_client(config)
    if compartment_id == None:
        compartment_id = config["tenancy"]
    groups = identity_client.list_groups(compartment_id).data
    group = None
    for group_aux in groups :
        if group_aux.name == group_name:
            LOG.info("Group found!")
            group = group_aux
            break
    LOG.info("[End] Get Group")
    return group


def delete_group(config, group_name):
    LOG.info("[START] Deleting Group '{0}'".format(group_name))
    identity_client = get_identity_client(config)
    group = get_group(config, group_name)
    LOG.info("Deleting group id '{0}'".format(group.id))
    result = identity_client.delete_group(group.id)
    LOG.info(result)
    LOG.info("Status : '{0}'".format(result.status))
    LOG.info("[END] Delete Group")
    return result


def get_user(config, user_name, compartment_id = None):
    LOG.info("[START] Get User '{0}'".format(user_name))
    identity_client = get_identity_client(config)
    if compartment_id == None:
        compartment_id = config["tenancy"]
    users = identity_client.list_users(compartment_id).data
    user = None
    for user_aux in users :
        if user_aux.name == user_name:
            LOG.info("User found!")
            user = user_aux
            break
    LOG.info("[End] Get User")
    return user


def create_user(config, compartment_id, user_name, description = "Generic description"):
    LOG.info("[START] Create User '{0}'".format(user_name))
    LOG.info("Compartment ID: '{0}'".format(compartment_id))
    LOG.info("Description: '{0}'".format(description))
    identity_client = get_identity_client(config)
    user_details = oci.identity.models.CreateUserDetails(
        compartment_id = compartment_id,
        name = user_name,
        description = description
        )
    user_response = identity_client.create_user(user_details)
    LOG.info(user_response.data)
    LOG.info("[END] Create User")
    return user_response.data


def delete_user(config, user_name):
    LOG.info("[START] Delete User '{0}'".format(user_name))
    identity_client = get_identity_client(config)
    user_id = get_user(config, user_name).id
    identity_client.delete_user(user_id)
    LOG.info("[END] Delete User")
    return


def add_user(config, group_name, user_name):
    LOG.info("[START] Add user to group")
    LOG.info("Group name: '{0}'".format(group_name))
    LOG.info("User name: '{0}'".format(user_name))
    identity_client = get_identity_client(config)

    # Get User and Group
    user = get_user(config, user_name)
    group = get_group(config, group_name)

    # Set details to add user
    add_details = oci.identity.models.AddUserToGroupDetails(
        user_id  = user.id,
        group_id  = group.id
    )

    # Add user
    LOG.info("[END] Adding user to group")
    membership = identity_client.add_user_to_group(add_details).data

    LOG.info(membership)
    LOG.info("[END] Add user to group")

def create_or_reset_password(config,user_name,compartment_id = None):
    LOG.info("[START] Create the password for '{0}' ".format(user_name))
    user = get_user(config, user_name)
    identity_client = get_identity_client(config)
    password = identity_client.create_or_reset_ui_password(user.id)
    LOG.info("[END] Create the password for '{0}' ".format(user_name))             
    LOG.info(password)
    return password

def get_key(config, user_name, key):
    LOG.info("[START] Get fingerprint for user '{0}'".format(user_name))
    LOG.info("Key is : '{0}'".format(key))
    user_id = get_user(config, user_name)
    identity_client = get_identity_client(config)
    key_response = identity_client.list_api_keys(user_id)
    keys = key_response.data
    key = None
    for key in keys:
        if key.key_value == key:
            LOG.info("Found Key")
            break 
    return key


def upload_api_key(config, user_name, key):
    LOG.info("[START] Upload API Key for User '{0}'".format(user_name))
    identity_client = get_identity_client(config)
    key_details = oci.identity.models.CreateApiKeyDetails(
        key = key
        )
    LOG.info(key_details)
    user_id = get_user(config, user_name).id
    key_response = identity_client.upload_api_key(
        user_id = user_id,
        create_api_key_details = key_details
        )
    LOG.info(key_response.data)
    LOG.info("[END] Upload API Key for user")
    return key_response.data


def delete_api_key(config, user_name, key):
    LOG.info("[START] Delete API Key for User '{0}'".format(user_name))
    LOG.info("Key is : '{0}'".format(key))
    identity_client = get_identity_client(config)
    user_id = get_user(config, user_name).id
    fingerprint = get_key(config, user_name, key).fingerprint
    identity_client.delete_api_key(
        user_id = user_id,
        fingerprint = fingerprint
        )
    LOG.info("[END] Delete API Key for user")
    return

## define tag
def get_tag_namespace_instance(config,compartment_id,tag_namespace_name):
    LOG.info("[START] Get Tag NameSpace")
    LOG.info("Tag NameSpace is: '{0}'".format(tag_namespace_name))
    LOG.info("Compartment ID: '{0}'".format(compartment_id))     
    identity_client = get_identity_client(config)
    
    instances = identity_client.list_tag_namespaces(compartment_id)
    
    for instance in instances:
        if instance.name ==  tag_namespace_name:
            LOG.info("Instance found")
            break
    LOG.info(instance)
    LOG.info("[END] Get Tag NameSpace")     
    return instance

def get_tag_instance(config,compartment_id,tag_namespace_name,tag_name):
    LOG.info("[START] Get tag ")
    LOG.info("Tag is: '{0}'".format(tag_name))
    LOG.info("Tag NameSpace is: '{0}'".format(tag_namespace_name))     
    identity_client = get_identity_client(config)
    
    tag_namespace = get_tag_namespace_instance(config,compartment_id,tag_namespace_name)
    instances = identity_client.list_tags(tag_namespace.id)
    for instance in instances:
        if instance.name ==  tag_name:
            LOG.info("Tag found")
            
    LOG.info(instance)
    LOG.info("[END] Get Tag ")  
    
    return instance

def create_tag_namespace(config,compartment_id,tag_namespace_name,description):
    LOG.info("[START] Create Tag NameSpace")
    identity_client = get_identity_client(config)
    
    tag_namespace_details = oci.identity.models.CreateTagNamespaceDetails(
        compartment_id = compartment_id,
        description = description,
        name = tag_namespace_name
        )
    instance_response = identity_client.create_tag_namespace(tag_namespace_details)
    LOG.info("[END] Create Tag NameSpace")    
    return instance_response.data

def create_tag(config,compartment_id,tag_namespace_name,tag_name,description):
    LOG.info("[START] Create tag in '{0}' ".format(tag_namespace_name))
    identity_client=get_identity_client(config)
    
    tag_details = oci.identity.models.CreateTagDetails(
        description = description,
        name = tag_name        
        )
    tag_namespace = get_tag_namespace_instance(config, compartment_id, tag_namespace_name)
    if tag_namespace.id == None:
       LOG.info("Can't find Specific Tag NameSpace") 
       return
    
    instance_response = identity_client.create_tag(
        tag_namespace_id = tag_namespace.id,
        create_tag_details = tag_details
        )
    LOG.info("[END] Create tag in '{0}' ".format(tag_namespace_name))    
    return instance_response.data

## is_retire as "true" or "false"
def update_tag_namespace(config,compartment_id,tag_namespace_name,is_retired):
    LOG.info("[START] Update the tag_namespace :'{0}' ".format(tag_namespace_name))
    identity_client=get_identity_client(config)
    tag_namespace_id = get_tag_namespace_instance(config, compartment_id, tag_namespace_name)
    update_details = oci.identity.models.UpdateTagNamespaceDetails(
        is_retired = is_retired
        )
    update_instance = identity_client.update_tag_namespace(
        tag_namespace_id = tag_namespace_id,
        update_tag_namespace_details = update_details 
        )
    LOG.info("[END] Update the tag_namespace")
    LOG.info(update_instance.data)
    return 

def update_tag(config,compartment_id,tag_namespace_name,tag_name,is_retired):
    LOG.info("[START] Update the tag : '{0}' ".format(tag_name))
    identity_client=get_identity_client(config)
    tag_namespace_id = get_tag_namespace_instance(config, compartment_id, tag_namespace_name)
    
    update_details = oci.identity.models.UpdateTagDetails(
        is_retired = is_retired
        )
    update_instance = identity_client.update_tag(
        tag_namespace_id = tag_namespace_id,
        tag_name = tag_name, 
        update_tag_details = update_details
        )
    LOG.info("[END] Update the tag")
    LOG.info(update_instance.data)
    return
