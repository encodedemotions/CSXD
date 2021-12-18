import re
import subprocess
import winreg


def check_custom_item(custom_item_dict, result_dict):
    if 'type' not in custom_item_dict:
        result_dict["unknown"][custom_item_dict["description"]] = {'reason': f"Custom item has no type.",
                                                                   'custom_item': custom_item_dict}
    item_type = custom_item_dict['type']
    if item_type in switch_dict:
        switch_dict[item_type](custom_item_dict, result_dict)
    else:
        result_dict["unknown"][custom_item_dict["description"]] = {'reason': f"Unsupported check type:{item_type}",
                                                                   'custom_item': custom_item_dict}


def check_registry_setting(custom_item_dict, result_dict):
    return_dict = {'custom_item': custom_item_dict}
    registry = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)
    key_to_read = custom_item_dict['reg_key'].strip('"').replace("HKLM", "").strip('\\')
    subkey_name = custom_item_dict['reg_item'].strip('"')
    directory_and_subkey = key_to_read + '\\' + subkey_name
    try:
        reg_item = winreg.OpenKey(registry, key_to_read)
        subkey_value = winreg.QueryValueEx(reg_item, subkey_name)
    except:
        subkey_value = None

    if subkey_value is None:
        reg_option = custom_item_dict['reg_option']

        if reg_option == "CAN_NOT_BE_NULL" or reg_option == "MUST_EXIST":
            return_dict['reason'] = f"Value or directory is NULL, reg_option:{reg_option}"
            return_dict['real_value'] = "NULL"
            if 'value_data' in custom_item_dict:
                return_dict['expected_value'] = custom_item_dict['value_data'].strip('"')
            result_dict['failed'][directory_and_subkey] = return_dict
            return
        if reg_option == "CAN_BE_NULL":
            return_dict['reason'] = f"Value or directory is NULL, reg_option:{reg_option}"
            return_dict['real_value'] = "NULL"
            if 'value_data' in custom_item_dict:
                return_dict['expected_value'] = custom_item_dict['value_data'].strip('"')
            result_dict['passed'][directory_and_subkey] = return_dict
            return

    if 'check_type' in custom_item_dict:
        if custom_item_dict['check_type'] == 'CHECK_REGEX':
            re_pattern = custom_item_dict['value_data'].strip('"')
            reg_data = str(subkey_value[0])
            result = re.search(re_pattern, reg_data)
            if result:
                return_dict['reason'] = f"Regex:'{re_pattern}' did match value_data:'{reg_data}'"
                return_dict['real_value'] = reg_data
                result_dict['passed'][directory_and_subkey] = return_dict
            else:
                return_dict['reason'] = f"Regex:'{re_pattern}' did not match value_data:'{reg_data}'"
                return_dict['real_value'] = reg_data
                result_dict['failed'][directory_and_subkey] = return_dict
            return
    if 'value_data' in custom_item_dict:
        value_data = custom_item_dict['value_data'].strip('"')
        reg_data = str(subkey_value[0])
        if value_data == reg_data:
            return_dict['reason'] = f"reg_data:{reg_data} == value_data:{value_data}"
            return_dict['real_value'] = reg_data
            return_dict['expected_value'] = value_data
            result_dict['passed'][directory_and_subkey] = return_dict
        else:
            return_dict['reason'] = f"reg_data:{reg_data} != value_data:{value_data}"
            return_dict['real_value'] = reg_data
            return_dict['expected_value'] = value_data
            result_dict['failed'][directory_and_subkey] = return_dict
        return


def reg_check(custom_item_dict, result_dict):
    return_dict = {'custom_item': custom_item_dict}
    registry = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)
    key_to_read = custom_item_dict['value_data'].strip('"').replace("HKLM", "").strip('\\')
    subkey_name = custom_item_dict['key_item'].strip('"')
    directory_and_subkey = key_to_read + '\\' + subkey_name

    try:
        reg_item = winreg.OpenKey(registry, key_to_read)
        subkey_value = winreg.QueryValueEx(reg_item, subkey_name)
    except:
        reg_option = custom_item_dict['reg_option']
        return_dict['reason'] = f"Value or directory is NULL, reg_option:{reg_option}"
        if reg_option == "MUST_EXIST":
            result_dict['failed'][directory_and_subkey] = return_dict
        else:
            result_dict['passed'][directory_and_subkey] = return_dict


switch_dict = {
    'REGISTRY_SETTING': check_registry_setting,
    'REG_CHECK': reg_check,
}

backup_dict = {}


def write_registry(check_dict):
    backup_registry(check_dict)
    failed_check_dict = check_dict['failed']
    reg_write(failed_check_dict)


def reg_write(failed_check_dict, restore=False):
    registry = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)
    if restore:
        for fail_name, fail_dict in failed_check_dict.items():
            real_value = fail_dict['real_value']
            custom_item = fail_dict['custom_item']
            if real_value == 'NULL':
                query = 'reg delete "' + custom_item['reg_key'] + '" /v ' + custom_item['reg_item'] + ' /d "' + \
                        real_value + '" /f'
                subprocess.Popen(query,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.STDOUT)
            else:
                if 'value_data' in custom_item:
                    query = 'reg add "' + custom_item['reg_key'] + '" /v ' + custom_item['reg_item'] + ' /d "' + \
                            real_value + '" /f'
                    subprocess.Popen(query,
                                     stdout=subprocess.PIPE,
                                     stderr=subprocess.STDOUT)
    else:
        for fail_name, fail_dict in failed_check_dict.items():
            custom_item = fail_dict['custom_item']
            if 'value_data' in custom_item:
                query = 'reg add "' + custom_item['reg_key'] + '" /v ' + custom_item['reg_item'] + ' /d "' + \
                        custom_item[
                            'value_data'] + '" /f'
                subprocess.Popen(query,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.STDOUT)


def backup_registry(check_dict):
    global backup_dict
    failed_check_dict = check_dict['failed']
    backup_dict = failed_check_dict


def restore_registry(current_dict):
    reg_write(backup_dict, restore=True)
