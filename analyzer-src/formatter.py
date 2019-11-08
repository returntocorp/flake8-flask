#!/usr/bin/env python3

import json
import os
import sys


def make_results(json, base_path):
    output = []
    for _, findings in json.items():
        if len(findings) == 0:
            continue
        """
        {
          "code": "R2C001",
          "filename": "/Users/ulziibayarotgonbaatar/Workspace/echelon-backend/r2c/batch/lib/util.py",
          "line_number": 26,
          "column_number": 13,
          "text": "Insecure HTTP URL http://169.254.169.254/latest/meta-data/instance-id",
          "physical_line": "            \"http://169.254.169.254/latest/meta-data/instance-id\"\n"
        }
        """
        for element in findings:
            filename = element["filename"]
            filename = os.path.relpath(filename, base_path)
            if filename.startswith("./"):
                filename = filename[2:]

            obj = {
                "check_id": element["code"],
                "path": filename,
                "start": {
                    "line": element.get("line_number", 0),
                    "col": element.get("column_number", 0),
                },
                "extra": {"text": element.get("text", "")},
            }
            output.append(obj)
    return output


def format_json(json_output, stream, base):
    results = make_results(json_output, base)
    obj = {"results": results}
    json.dump(obj, stream, indent=4, separators=(",", ": "))


if __name__ == "__main__":
    base = sys.argv[1]
    json_output = json.loads(sys.stdin.read())
    format_json(json_output, sys.stdout, base)
