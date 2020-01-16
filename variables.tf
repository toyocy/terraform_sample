data "vsphere_virtual_machine" "template" {
  name          = "<tempalte name>"
  datacenter_id = "${data.vsphere_datacenter.dc.id}"
}

data "vsphere_datacenter" "dc" {
  name = "<vsphere DC name>"
}

data "vsphere_compute_cluster" "cluster" {
  name          = "<vsphere CL name>"
  datacenter_id = "${data.vsphere_datacenter.dc.id}"
}

data "vsphere_datastore" "datastore" {
  name          = "shared_datastore"
  datacenter_id = "${data.vsphere_datacenter.dc.id}"
}

data "vsphere_network" "network" {
  name          = "VM Network"
  datacenter_id = "${data.vsphere_datacenter.dc.id}"
}

variable "vsphere_user" {
  default = "<vsphere username>"
}

variable "vsphere_password" {
  default = <vsphere user password>"
}

variable "vsphere_server" {
  default = "<vsphere hostname>"
}
