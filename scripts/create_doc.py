#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import os
import json
import xlsxwriter


def fetch_tfstate(tfstate = ""):

    if tfstate == "":
        print("tfstate ファイルが存在しません。terraform apply を実行してください。")
        sys.exit(1)

    try:
        os.path.exists(tfstate)
    except Exception:
        print("tfstate ファイルを開けません。再度 terraform apply を実行してください。")
        sys.exit(1)

    with open(tfstate, mode='r', encoding='utf-8') as f:
        result = json.load(f)

    return result


def get_vms(config_data):
    resources = []
    for value in config_data:
        if value == 'resources':
            for index, item in enumerate(config_data[value]):
                if ("managed" in config_data[value][index].values()):
                    resources.append(item)

    return resources


def get_os_type(customize_dict, result):
    if 'windows_options' in customize_dict:
        result['os_type'] = 'Windows'
    elif 'linux_options' in customize_dict:
        result['os_type'] = 'Linux'

    return result


def set_network_interface_config(network_if, result):
    for index, interface in enumerate(network_if):
        result['interface'].append(index)
        result['interface'][index] = {}
        result['interface'][index]['ipv4_address'] = interface.get(
            'ipv4_address')
        result['interface'][index]['ipv4_netmask'] = interface.get(
            'ipv4_netmask')
        result['interface'][index]['ipv6_address'] = interface.get(
            'ipv6_address')
        result['interface'][index]['ipv6_netmask'] = interface.get(
            'ipv6_netmask')

    return result['interface']


def get_ip_config(customize_dict, result):
    result['ipv4_gateway'] = customize_dict.get('ipv4_gateway')
    result['ipv6_gateway'] = customize_dict.get('ipv6_gateway')
    result['dns_servers'] = customize_dict.get('dns_server_list')
    result['interface'] = []
    result['interface'] = set_network_interface_config(
        customize_dict['network_interface'], result)

    return result


def get_os_option(customize_dict, result):
    if result['os_type'] == 'Windows':
        os_options = 'windows_options'
        result['computer_name'] = customize_dict[os_options][0].get(
            'computer_name')
        result['workgroup'] = customize_dict[os_options][0].get('workgroup')
        result['domain'] = customize_dict[os_options][0].get('join_domain')
    elif result['os_type'] == 'Linux':
        os_options = 'linux_options'
        result['computer_name'] = customize_dict[os_options][0].get(
            'host_name')
        result['domain'] = customize_dict[os_options][0].get('domain')

    return result


def get_disk_config(vm_disk_info, result):
    for index, disk in enumerate(vm_disk_info):
        result['disk'].append(index)
        result['disk'][index] = {}
        result['disk'][index]['label'] = disk.get('label')
        result['disk'][index]['size'] = disk.get('size')
        if disk.get('thin_provisioned'):
            result['disk'][index]['disk_type'] = 'シンプロビジョニング'
        else:
            result['disk'][index]['disk_type'] = 'シックプロビジョニング'

    return result['disk']


def get_vm_configs(vm_meta_info, result):
    result['cpu'] = vm_meta_info.get('num_cpus')
    result['memory'] = vm_meta_info.get('memory')
    result['disk'] = []
    result['disk'] = get_disk_config(vm_meta_info['disk'], result)

    return result


def get_config_value(vm_resource):
    result = {}
    customize_dict = vm_resource['instances'][0]['attributes']['clone'][0]['customize'][0]
    result = get_os_type(customize_dict, result)
    result = get_ip_config(customize_dict, result)
    result = get_os_option(customize_dict, result)

    vm_meta_info = vm_resource['instances'][0]['attributes']
    result = get_vm_configs(vm_meta_info, result)

    return result


def set_resource_params(sheet, params, meta, text_format, label_format):
    HEADER_MARGIN = 3
    PARAMS_LABEL_COL = meta['base_col']
    PARAMS_MARGIN = 1
    PARAMS_COL = meta['base_col'] + PARAMS_MARGIN
    VALUE_COL = PARAMS_COL + 1

    params_row = 0
    params_name = meta['params_name']

    for i, resource in enumerate(params[params_name]):
        params_label_row = i + HEADER_MARGIN + params_row
        sheet.write(params_label_row, PARAMS_LABEL_COL, '%s %i' %
                    (meta['params_name'], i), label_format)

        for i, item in enumerate(meta['item']):
            params_row = i + params_label_row + 1
            sheet.write(
                params_row,
                PARAMS_COL,
                meta['item'].get(item),
                text_format)
            sheet.write(params_row, VALUE_COL, resource[item], text_format)

    if 'general_params' in meta:
        for ge_params in meta['general_params']:
            params_row += 1
            sheet.write(
                params_row,
                PARAMS_COL,
                meta['general_params'].get(ge_params),
                text_format)
            sheet.write(params_row, VALUE_COL, params[ge_params], text_format)

    return sheet


def set_params(params, sheet, text_format, label_format):
    sheet.write('C5', params['computer_name'], text_format)
    sheet.write('C6', '%s CPU' % params['cpu'], text_format)
    sheet.write('C7', '%s MB' % params['memory'], text_format)
    if params['os_type'] == 'Windows':
        sheet.write('C8', 'Windows Server 2016 Datacenter', text_format)
        sheet.write('C10', 'Administrator', text_format)
    else:
        sheet.write('C8', 'CentOS 7', text_format)
        sheet.write('C10', 'root', text_format)

    if params['workgroup'] is None:
        sheet.write('C9', params['domain'], text_format)
    else:
        sheet.write('C9', params['workgroup'], text_format)

    hdd_params_meta_info = {
        'params_name': 'disk',
        'base_col': 4,
        'item': {
            'label': 'ディスクラベル',
            'size': '容量',
            'disk_type': 'ディスクタイプ',
        }
    }

    interface_params_meta_info = {
        'params_name': 'interface',
        'base_col': 8,
        'item': {
            'ipv4_address': 'IPv4 アドレス',
            'ipv4_netmask': 'IPv4 サブネットマスク',
            'ipv6_address': 'IPv6 アドレス',
            'ipv6_netmask': 'IPv6 サブネットマスク',
        },
        'general_params': {
            'ipv4_gateway': 'IPv4 ゲートウェイ',
            'ipv6_gateway': 'IPv6 ゲートウェイ',
            'dns_servers': 'DNSサーバー',
        }
    }

    sheet = set_resource_params(
        sheet,
        params,
        hdd_params_meta_info,
        text_format,
        label_format)
    sheet = set_resource_params(
        sheet,
        params,
        interface_params_meta_info,
        text_format,
        label_format)

    return sheet


def set_params_table(params, workbook):
    sheet = workbook.add_worksheet(params['computer_name'])

    header_format = workbook.add_format(
        {
            'font_name': 'Meiryo UI',
            'bold': True,
            'font_size': 18
        }
    )

    title_format = workbook.add_format(
        {
            'font_name': 'Meiryo UI',
            'bold': True,
            'font_color': 'white',
            'bg_color': '#1F497D',
            'font_size': 10,
        }
    )

    text_format = workbook.add_format(
        {
            'font_name': 'Meiryo UI',
            'bold': False,
            'font_size': 10,
            'align': 'right',
        }
    )

    label_format = workbook.add_format(
        {
            'font_name': 'Meiryo UI',
            'bold': False,
            'font_size': 10,
        }
    )

    sheet.set_column('A:A', 2)
    sheet.set_column('B:B', 20)
    sheet.set_column('C:C', 35)
    sheet.set_column('D:D', 2)
    sheet.set_column('E:E', 2)
    sheet.set_column('F:F', 15)
    sheet.set_column('G:G', 20)
    sheet.set_column('H:H', 2)
    sheet.set_column('I:I', 2)
    sheet.set_column('J:J', 15)
    sheet.set_column('K:K', 40)

    sheet.write('A1', '%s パラメータシート' % params['computer_name'], header_format)
    sheet.write('B3', 'サーバー構成', title_format)
    sheet.merge_range('B3:C3', None)
    sheet.write('B4', '設置拠点', text_format)
    sheet.write('B5', 'ホスト名', text_format)
    sheet.write('B6', 'CPU', text_format)
    sheet.write('B7', 'メモリ', text_format)
    sheet.write('B8', 'OS', text_format)
    sheet.write('B9', 'ドメイン', text_format)
    sheet.write('B10', '管理者アカウント', text_format)
    sheet.write('B11', '管理者パスワード', text_format)

    sheet.write('E3', 'HDD構成', title_format)
    sheet.merge_range('E3:G3', None)

    sheet.write('I3', 'ネットワーク構成', title_format)
    sheet.merge_range('I3:K3', None)

    sheet = set_params(params, sheet, text_format, label_format)

    return workbook


def create_datasheet(config_data):
    filename = 'パラメータシート.xlsx'
    workbook = xlsxwriter.Workbook(filename)
    vms = get_vms(config_data)

    for vm in vms:
        params = get_config_value(vm)
        workbook = set_params_table(params, workbook)

    workbook.close()


def main():
    base = os.path.dirname(os.path.abspath(__file__))
    tfstate = os.path.normpath(os.path.join(base, "../terraform.tfstate"))
    config_data = fetch_tfstate(tfstate)
    create_datasheet(config_data)


if __name__ == "__main__":
    main()
