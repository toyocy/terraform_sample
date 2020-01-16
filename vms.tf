# VM Config
locals {
  cpu-1        = 4
  memory-1     = 8
  windows_firm = "efi"
  linux_firm   = "bios"
}

#OS Config
locals {
  hostname              = "default-host"
  workgroup             = "WORKGROUP"
  domain                = "<domain name>"
  domain_admin_user     = ""
  domain_admin_password = ""
}

#Network Config
locals {
  ipv4_address-1 = ""
  ipv4_netmask-1 = 24
  ipv6_address-1 = ""
  ipv6_netmask-1 = 60
  ipv4_gateway   = ""
  ipv6_gateway   = ""
}

#Disk Config
locals {
  disk_lable-1            = "disk0"
  disk_size-1             = 200
  disk-1_thin_provisioned = false
  disk-1_eagerly_scrub    = false
}

#Template Config
locals {
  template = "<tempalte name>"
}

resource "vsphere_virtual_machine" "vm" {
  name             = "${local.hostname}"
  resource_pool_id = "${data.vsphere_compute_cluster.cluster.resource_pool_id}"
  datastore_id     = "${data.vsphere_datastore.datastore.id}"

  num_cpus = "${local.cpu-1}"
  memory   = "${local.memory-1}"
  firmware = "${local.windows_firm}"

  guest_id = "${data.vsphere_virtual_machine.template.guest_id}"

  scsi_type = "${data.vsphere_virtual_machine.template.scsi_type}"

  disk {
    label            = "${local.disk_lable-1}"
    size             = "${local.disk_size-1}"
    eagerly_scrub    = "${local.disk-1_eagerly_scrub}"
    thin_provisioned = "${local.disk-1_thin_provisioned}"
  }

  network_interface {
    network_id   = "${data.vsphere_network.network.id}"
    adapter_type = "${data.vsphere_virtual_machine.template.network_interface_types[0]}"
  }

  clone {
    template_uuid = "${data.vsphere_virtual_machine.template.id}"

    customize {
      windows_options {
        computer_name = "${local.hostname}"
        workgroup     = "${local.workgroup}"
      }

      network_interface {
        ipv4_address = "${local.ipv4_address-1}"
        ipv4_netmask = "${local.ipv4_netmask-1}"
      }
      ipv4_gateway = "${local.ipv4_gateway}"
    }
  }
}
