import re


def get_children_dicts(dictionary):
    for key, value in dictionary.items():
        if type(value) is dict:
            yield key, value


def get_modifiers(dictionary):
    has_modifiers = False
    for key, value in dictionary.items():
        if type(value) is dict:
            has_modifiers = True
            break

    if not has_modifiers:
        return None
    for key, value in dictionary.items():
        if type(value) is dict:
            continue
        else:
            yield key, value


check_name_re = "(_[0-9]+)"


def export_audit(file_stream, json_dict, name=None, indent_count=0, indent_size=2):
    def print_name(string):
        print(f"{' ' * indent_size * indent_count}{string}", end="", file=file_stream)

    def print_params(param_name, param_value):
        padding = (12 - len(param_name)) * " "
        print(f"{' ' * indent_size * (indent_count + 1)}{param_name + padding}:  {param_value}", file=file_stream)

    if name is None:
        name = next(iter(json_dict))
        dictionary = json_dict[name]
        export_audit(file_stream, dictionary, name)
        return

    print_name(f"<{name}")
    for modifier_name, modifier_value in get_modifiers(json_dict):
        if modifier_name != name:
            print(f"{modifier_name}:{modifier_value}", end="", file=file_stream)
        else:
            print(f":{modifier_value}", end="", file=file_stream)
    print(">", file=file_stream)

    got_children = False
    for dict_name, dictionary in get_children_dicts(json_dict):
        got_children = True
        re_result = re.search(check_name_re, dict_name)
        if re_result:
            dict_name = dict_name.strip(re_result.group(1))
        export_audit(file_stream, dictionary, dict_name, indent_count=indent_count + 1)

    if not got_children:
        for parameter_name, parameter_value in json_dict.items():
            print_params(parameter_name, parameter_value)
    print_name(f"</{name}>\n")
