import json
import pyjsonviewer
from audit_parser import get_json_from_audit

if __name__ == '__main__':
    input_file = "MSCT_Windows_10_2004_v1.0.0.audit"
    json_data = get_json_from_audit(input_file)
    # Save json dict to file
    with open(input_file.removesuffix(".audit")+'.json', 'w') as write_stream:
        json.dump(json_data, write_stream, indent=4)
    # View data with pyjsonviewer
    pyjsonviewer.view_data(json_data=json_data)
