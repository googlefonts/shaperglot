# Check all crates have the same version number
import os
import subprocess
import json
import re

if "CRATE_PATTERN" not in os.environ:
    print("CRATE_PATTERN environment variable not set")
    exit(1)
crate_pattern = os.environ.get("CRATE_PATTERN", ".*")
metadata = json.loads(
    subprocess.check_output(
        ["cargo", "metadata", "--no-deps", "--format-version=1"]
    ).decode("utf-8")
)
members = {
    k["name"]: k["version"]
    for k in metadata["packages"]
    if re.match("^" + crate_pattern + "$", k["name"])
}
if len(set(members.values())) > 1:
    print("Crates have different versions:")
    for name, version in members.items():
        print(f" - {name}: {version}")
    exit(1)
print("All crates have the same version:", members)
exit(0)
