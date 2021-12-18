import re

content_match_re = r'\n(?!#)\s*<([0-9a-zA-Z_]+)((?:\s*(?:[0-9a-zA-Z_]*):(?:[0-9a-zA-Z_" ]+))*)>((?:[^<]|(?:</?(?!\1)[0-9a-zA-Z_ :"]+>))+)(?=</\1>)'
modifier_re = '([^:]*):((?:[^:" ]+)|(?:"[^:"]*?"))'
property_re = '\s+([0-9a-zA-Z_]+)\s+:\s+((?:"[^"]*")|(?:[0-9a-zA-Z_]+))'


def parse_match(child_match):
    dictionary = {}
    name = child_match.group(1)
    # dictionary['name'] = name
    modifiers = child_match.group(2)
    match_content = child_match.group(3)

    for modifier_match in re.finditer(modifier_re, modifiers):
        modifier_name = modifier_match.group(1)
        if len(modifier_name) == 0:
            modifier_name = name
        modifier_value = modifier_match.group(2)
        dictionary[modifier_name] = modifier_value

    has_children = False
    child_matches = re.finditer(content_match_re, match_content)
    for child_match in child_matches:
        child_name, child_dict = parse_match(child_match)
        has_children = True
        if child_name in dictionary:
            i = 1
            while child_name + '_' + str(i) in dictionary:
                i += 1
            dictionary[child_name + '_' + str(i)] = child_dict
        else:
            dictionary[child_name] = child_dict
    if not has_children:
        for prop in re.finditer(property_re, match_content):
            dictionary[prop.group(1)] = prop.group(2)

    return name, dictionary


def audit_parser(contents):
    content_matches = re.finditer(content_match_re, contents)
    for content_match in content_matches:
        name, output_dict = parse_match(content_match)
        return output_dict

    return None


def get_json_from_audit(filename):
    stream = open(filename, 'r')
    file_contents = stream.read()
    return audit_parser(file_contents)
