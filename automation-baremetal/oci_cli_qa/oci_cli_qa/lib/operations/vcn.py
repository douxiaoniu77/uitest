'''
Created on Mar 6, 2018
@author: umartine

===============================================================================
                                     Change log
===============================================================================

    Date         GUID        Comment
    ----------------------------------------------------------------
    2018-03-06   umartine    Initial creation
    2018-03-09   umartine    Adding loging and Security list logic
    2018-03-12   umartine    Add DNS labels to VCN and Subnets
    2018-03-13   umartine    Re-packing operations lib
    2018-03-14   umartine    Add get_subnet operation
    2018-03-14   umartine    Display IP Address
    2018-03-16   umartine    Add support to pick subnet by AD
    2018-03-21   umartine    Create routing rule for reachability
    2018-04-02   umartine    Add list subnet method
    2018-05-24   umartine    Get Private IP's for mount targets
    2018-01-04   umartine    Provide logs of the newly created vcn

'''

import oci

import oci_cli_qa.lib.operations.identity as identity
from oci_cli_qa.lib.logger import LOG


def get_vcn_client(config):
    LOG.info("Get VCN Client")
    return oci.core.virtual_network_client.VirtualNetworkClient(config)


def get_private_ip(config, ip_id):
    LOG.info("[START] Get Private IP")
    LOG.info("IP Identifier: '{0}'".format(ip_id))
    vcn_client = get_vcn_client(config)
    private_ip = vcn_client.get_private_ip(ip_id).data
    LOG.info(private_ip)
    LOG.info("[END] Get Private IP")
    return private_ip


def create_vcn(config, compartment_id, display_name = "automation_vcn", cidr_block="10.0.0.0/16"):
    LOG.info("[START] Create new VCN '{0}'".format(display_name))
    LOG.info("Compartment ID: '{0}'".format(compartment_id))
    LOG.info("CIDR Block: '{0}'".format(cidr_block))
    vcn_client = get_vcn_client(config)
    dns_label = display_name.replace("_", "")
    vcn_details = oci.core.models.CreateVcnDetails(
        cidr_block = cidr_block,
        compartment_id = compartment_id,
        display_name = display_name,
        dns_label = dns_label
        )
    vcn_response = vcn_client.create_vcn(vcn_details)
    LOG.info(vcn_response.data)
    LOG.info("[END] Create new VCN")
    return vcn_response.data   


def create_subnet(config, availability_domain, cidr_block, compartment_id, display_name, vcn):
    LOG.info("[START] Create new subnet '{0}'".format(display_name))
    LOG.info("Compartment ID: '{0}'".format(compartment_id))
    LOG.info("VCN id: '{0}'".format(vcn.id))
    LOG.info("CIDR Block: '{0}'".format(cidr_block))
    LOG.info("Availability Domain: '{0}'".format(availability_domain))
    dns_label = display_name.replace("_", "")
    vcn_client = get_vcn_client(config)
    subnet_details = oci.core.models.CreateSubnetDetails(
        availability_domain = availability_domain.name,
        cidr_block = cidr_block,
        compartment_id = compartment_id,
        display_name = display_name,
        vcn_id = vcn.id,
        dns_label = dns_label
        )
    subnet_response = vcn_client.create_subnet(subnet_details)
    LOG.info(subnet_response.data)
    LOG.info("[END] Create new subnet")
    return subnet_response.data


def create_internet_gateway(config, compartment_id, vcn):
    LOG.info("[START] Create new gateway")
    LOG.info("Compartment ID: '{0}'".format(compartment_id))
    LOG.info("VCN id: '{0}'".format(vcn.id))
    vcn_client = get_vcn_client(config)
    gateway_details = oci.core.models.CreateInternetGatewayDetails(
        compartment_id = compartment_id,
        is_enabled = True,
        vcn_id = vcn.id
        )
    gateway_response = vcn_client.create_internet_gateway(gateway_details)
    LOG.info(gateway_response.data)
    LOG.info("[END] Create new gateway")
    return gateway_response.data


def get_security_list(config, compartment_id, security_list_name, vcn):
    LOG.info("[START] Get security list")
    LOG.info("Security List Name '{0}'".format(security_list_name))
    LOG.info("Compartment ID '{0}'".format(compartment_id))
    vcn_client = get_vcn_client(config)
    seclist_response = vcn_client.list_security_lists(compartment_id, vcn.id)
    security_lists = seclist_response.data
    LOG.info("Security List count '{0}'".format(len(security_lists)))
    security_list = None
    for security_list_aux in security_lists:
        if security_list_aux.display_name == security_list_name:
            security_list = security_list_aux
            LOG.info("Security list found")
            break
    LOG.info(security_list)
    LOG.info("[END] Get security list")
    return security_list


def list_subnets(config, compartment_id, vcn_id):
    LOG.info("[START] List subnets")
    LOG.info("Compartment ID '{0}'".format(compartment_id))
    LOG.info("VCN ID '{0}'".format(vcn_id))
    vcn_client = get_vcn_client(config)
    subnets = vcn_client.list_subnets(compartment_id, vcn_id).data
    LOG.info("[END] List subnets")
    return subnets


def get_subnet(config, compartment_id, vcn_id, subnet_name_pattern = "", ad = None):
    LOG.info("[START] Get subnet")
    LOG.info("Security List Name Pattern '{0}'".format(subnet_name_pattern))
    LOG.info("Availability Domain '{0}'".format(ad))
    LOG.info("Compartment ID '{0}'".format(compartment_id))
    LOG.info("VCN ID '{0}'".format(vcn_id))
    subnets = list_subnets(config, compartment_id, vcn_id)
    subnet = None
    for subnet_aux in subnets:
        if subnet_name_pattern in subnet_aux.display_name:
            if ad == None or ad in subnet_aux.availability_domain:
                subnet = subnet_aux
                LOG.info("Subnet found")
                break
    LOG.info(subnet)
    LOG.info("[END] Get subnet")
    return subnet

def get_vcn(config, compartment_id, vcn_name):
    LOG.info("[START] Get VCN")
    LOG.info("VCN name '{0}'".format(vcn_name))
    LOG.info("Compartment ID '{0}'".format(compartment_id))
    vcn_client = get_vcn_client(config)
    vcns = vcn_client.list_vcns(compartment_id).data
    vcn_out = None
    for vcn_aux in vcns:
        if vcn_name == vcn_aux.display_name:
            vcn_out = vcn_aux
            LOG.info("VCN found")
            break
    LOG.info(vcn_out)
    LOG.info("[END] Get VCN")
    return vcn_out


def get_vnic(config, vnic_id):
    LOG.info("[START] Get VNIC: '{0}'".format(vnic_id))
    vcn_client = get_vcn_client(config)
    vnic = vcn_client.get_vnic(vnic_id).data
    LOG.info(vnic)
    LOG.info("[END] Get VNIC")
    return vnic


def update_security_list(config, security_list_id, ingress_rules, egress_rules):
    LOG.info("[START] Update Security List")
    LOG.info("Security List: '{0}'".format(security_list_id))
    LOG.info("Ingress rules count: '{0}'".format(len(ingress_rules)))
    LOG.info("Egress rules count: '{0}'".format(len(egress_rules)))
    vcn_client = get_vcn_client(config)
    update_seclist_details = oci.core.models.UpdateSecurityListDetails(
        egress_security_rules = egress_rules,
        ingress_security_rules = ingress_rules
        )
    seclist_response = vcn_client.update_security_list(security_list_id, update_seclist_details)
    LOG.info(seclist_response.data)
    LOG.info("[END] Update Security List")
    return seclist_response.data


def create_port_range(port_range):
    if port_range == None:
        return None
    return oci.core.models.PortRange(min = port_range[0], max = port_range[1])


def create_TCP_ingress_rule(source, source_port_range = None,  destination_port_range = None):
    LOG.info("[START] Create TCP ingress Rule")
    LOG.info("Source: '{0}'".format(source))
    LOG.info("Source Port Range: '{0}'".format(source_port_range))
    LOG.info("Destination Port Range: '{0}'".format(destination_port_range))
    options = oci.core.models.TcpOptions(
        destination_port_range = create_port_range(destination_port_range),
        source_port_range = create_port_range(source_port_range)
        )
    rule = oci.core.models.IngressSecurityRule(protocol = "6",
                                               source = source,
                                               tcp_options = options
                                               )
    LOG.info("[END] Create TCP ingress Rule")
    return rule


def create_TCP_egress_rule(destination, source_port_range = None,  destination_port_range = None):
    LOG.info("[START] Create TCP egress Rule")
    LOG.info("Destination: '{0}'".format(destination))
    LOG.info("Source Port Range: '{0}'".format(source_port_range))
    LOG.info("Destination Port Range: '{0}'".format(destination_port_range))
    options = oci.core.models.TcpOptions(
        destination_port_range = create_port_range(destination_port_range),
        source_port_range = create_port_range(source_port_range)
        )
    rule = oci.core.models.EgressSecurityRule(protocol = "6",
                                               destination = destination,
                                               tcp_options = options
                                               )
    LOG.info("[END] Create TCP egress Rule")
    return rule


def create_UDP_ingress_rule(source, source_port_range = None,  destination_port_range = None):
    LOG.info("[START] Create UDP ingress Rule")
    LOG.info("Source: '{0}'".format(source))
    LOG.info("Source Port Range: '{0}'".format(source_port_range))
    LOG.info("Destination Port Range: '{0}'".format(destination_port_range))
    options = oci.core.models.UdpOptions(
        destination_port_range = create_port_range(destination_port_range),
        source_port_range = create_port_range(source_port_range)
        )
    rule = oci.core.models.IngressSecurityRule(protocol = "17",
                                               source = source,
                                               udp_options = options
                                               )
    LOG.info("[END] Create UDP ingress Rule")
    return rule


def create_UDP_egress_rule(destination, source_port_range = None,  destination_port_range = None):
    LOG.info("[START] Create UDP egress Rule")
    LOG.info("Destination: '{0}'".format(destination))
    LOG.info("Source Port Range: '{0}'".format(source_port_range))
    LOG.info("Destination Port Range: '{0}'".format(destination_port_range))
    options = oci.core.models.UdpOptions(
        destination_port_range = create_port_range(destination_port_range),
        source_port_range = create_port_range(source_port_range)
        )
    rule = oci.core.models.EgressSecurityRule(protocol = "17",
                                               destination = destination,
                                               udp_options = options
                                               )
    LOG.info("[END] Create UDP egress Rule")
    return rule


def create_ICMP_options(icmp_type = None, code = None):
    if icmp_type == None:
        return None
    return oci.core.models.IcmpOptions(code = code, type = icmp_type)


def create_ICMP_ingress_rule(source, icmp_type = None, code = None):
    LOG.info("[START] Create ICMP ingress Rule")
    LOG.info("Source: '{0}'".format(source))
    LOG.info("Code: '{0}'".format(code))
    LOG.info("Type: '{0}'".format(icmp_type))
    options = create_ICMP_options(icmp_type = icmp_type, code = code)
    rule = oci.core.models.IngressSecurityRule(protocol = "1",
                                               source = source,
                                               icmp_options = options
                                               )
    LOG.info("[END] Create ICMP ingress Rule")
    return rule


def create_ICMP_egress_rule(destination, icmp_type = None, code = None):
    LOG.info("[START] Create ICMP egress Rule")
    LOG.info("Destination: '{0}'".format(destination))
    LOG.info("Code: '{0}'".format(code))
    LOG.info("Type: '{0}'".format(type))
    options = create_ICMP_options(icmp_type = icmp_type, code = code)
    rule = oci.core.models.EgressSecurityRule(protocol = "1",
                                               destination = destination,
                                               icmp_options = options
                                               )
    LOG.info("[END] Create ICMP egress Rule")
    return rule


def create_ALL_ingress_rule(source):
    LOG.info("[START] Create ALL ingress Rule")
    LOG.info("Source: '{0}'".format(source))
    rule = oci.core.models.IngressSecurityRule(protocol = "all",
                                               )
    LOG.info("[END] Create ALL ingress Rule")
    return rule


def create_ALL_egress_rule(destination):
    LOG.info("[START] Create ALL egress Rule")
    LOG.info("Destination: '{0}'".format(destination))
    rule = oci.core.models.EgressSecurityRule(protocol = "all",
                                               destination = destination
                                               )
    LOG.info("[END] Create ALL egress Rule")
    return rule

def create_route_rule(cidr_block, target_id):
    LOG.info("[Start] Create Route Rule")
    LOG.info("CIDR Block: {0}".format(cidr_block))
    LOG.info("Target ID: {0}".format(target_id))
    route_rule = oci.core.models.RouteRule( cidr_block = cidr_block,
                                            network_entity_id  = target_id)
    LOG.info(route_rule)
    LOG.info("[END] Create Route Rule")
    return route_rule


def update_route_table(config, rout_table_id, route_rules):
    LOG.info("[START] Update Route Table: '{0}'".format(rout_table_id))
    LOG.info("Route Table ID: {0}".format(rout_table_id))
    LOG.info("Rule Count: {0}".format(len(route_rules)))
    vcn_client = get_vcn_client(config)
    route_table_details = oci.core.models.UpdateRouteTableDetails(route_rules = route_rules)
    route_table = vcn_client.update_route_table(rout_table_id, route_table_details).data
    LOG.info(route_table)
    LOG.info("[END] Get Route Table")
    return route_table


def create_full_vcn(config, compartment_id, vcn_name = "PAAS_VCN"):
    LOG.info("[START] Create VCN with resources")
    ###############################################
    # Create VCN
    ###############################################
    LOG.info("Create VCN")
    vcn = create_vcn(config, compartment_id, vcn_name)

    ###############################################
    # Create Subnets
    ###############################################
    # Get AD
    LOG.info("Get both AD names")
    ad1 = identity.get_availability_domain(config, "AD-1")
    ad2 = identity.get_availability_domain(config, "AD-2")
    
    # CIDR Blocks
    LOG.info("Create Subnets")
    cidr = ["10.0.{0}.0/24".format(i) for i in xrange(4)]
    create_subnet(config, ad1, cidr[0], compartment_id, "sn_ad1", vcn)
    create_subnet(config, ad1, cidr[1], compartment_id, "sn_ad1_backup", vcn)
    create_subnet(config, ad2, cidr[2], compartment_id, "sn_ad2", vcn)
    create_subnet(config, ad2, cidr[3], compartment_id, "sn_ad2_backup", vcn)
    
    ###############################################
    # Create Gateway compartment
    ###############################################
    LOG.info("Create VCN")
    internet_gateway = create_internet_gateway(config, compartment_id, vcn)
    
    ###############################################
    # Update security rules
    ###############################################
    LOG.info("Update Security List")
    security_list_id = vcn.default_security_list_id
    
    LOG.info("Create ingress rules")
    ingress_rules = [create_TCP_ingress_rule(cidr_i) for cidr_i in cidr]
    ingress_rules += [create_ICMP_ingress_rule(cidr_i) for cidr_i in cidr]
    ingress_rules.append(create_TCP_ingress_rule("0.0.0.0/0", destination_port_range = (22, 22)))
    ingress_rules.append(create_ICMP_ingress_rule("0.0.0.0/0", icmp_type = 3, code = 4))
    ingress_rules.append(create_ICMP_ingress_rule("10.0.0.0/16", icmp_type = 3))
    
    LOG.info("Create egress rules")
    egress_rules = [create_TCP_egress_rule(cidr_i) for cidr_i in cidr]
    egress_rules += [create_ICMP_egress_rule(cidr_i) for cidr_i in cidr]
    egress_rules.append(create_ALL_egress_rule("0.0.0.0/0"))
    
    LOG.info("Update Security list")
    update_security_list(config, security_list_id, ingress_rules, egress_rules)

    ###############################################
    # Update route rules
    ###############################################
    LOG.info("Update Route Rules")
    rout_table_id = vcn.default_route_table_id
    default_route_rule = create_route_rule("0.0.0.0/0", internet_gateway.id)
    route_rules = [default_route_rule]
    update_route_table(config, rout_table_id, route_rules)
    LOG.info(vcn)
    LOG.info("[END] Create VCN with resources")
    return vcn
