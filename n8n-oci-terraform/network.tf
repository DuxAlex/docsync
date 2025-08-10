resource "oci_core_virtual_network" "vcn" {
  compartment_id = var.compartment_id
  cidr_block     = "10.0.0.0/16"
  display_name   = "n8n-vcn"
  dns_label      = "n8nvcn"
}

resource "oci_core_internet_gateway" "igw" {
  compartment_id = var.compartment_id
  vcn_id         = oci_core_virtual_network.vcn.id
  display_name   = "n8n-igw"
}

resource "oci_core_route_table" "route_table" {
  compartment_id = var.compartment_id
  vcn_id         = oci_core_virtual_network.vcn.id
  display_name   = "n8n-rt"

  route_rules {
    network_entity_id = oci_core_internet_gateway.igw.id
    destination       = "0.0.0.0/0"
    destination_type  = "CIDR_BLOCK"
  }
}

resource "oci_core_security_list" "n8n_sl" {
  compartment_id = var.compartment_id
  vcn_id         = oci_core_virtual_network.vcn.id
  display_name   = "n8n-sl"

  ingress_security_rules {
    protocol  = "6" // TCP
    source    = "0.0.0.0/0"
    stateless = false

    tcp_options {
      min = 22
      max = 22
    }
  }

  ingress_security_rules {
    protocol  = "6" // TCP
    source    = "0.0.0.0/0"
    stateless = false

    tcp_options {
      min = 80
      max = 80
    }
  }

  ingress_security_rules {
    protocol  = "6" // TCP
    source    = "0.0.0.0/0"
    stateless = false

    tcp_options {
      min = 443
      max = 443
    }
  }
}

resource "oci_core_subnet" "subnet" {
  compartment_id             = var.compartment_id
  vcn_id                     = oci_core_virtual_network.vcn.id
  cidr_block                 = "10.0.1.0/24"
  display_name               = "n8n-subnet"
  route_table_id             = oci_core_route_table.route_table.id
  security_list_ids          = [oci_core_security_list.n8n_sl.id]
  prohibit_public_ip_on_vnic = false
  dns_label                  = "n8nsubnet"
}