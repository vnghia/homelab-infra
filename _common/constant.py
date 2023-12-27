import os
from pathlib import Path

import pulumi

PROJECT_ROOT_DIR = Path.cwd()

PROJECT_NAME = os.environ.get("PULUMI_PROJECT_NAME", pulumi.get_project())
PROJECT_STACK = pulumi.get_stack()
PROJECT_TAG = {
    "pulumi": "1",
    "pulumi.project": PROJECT_NAME,
    "pulumi.stack": PROJECT_STACK,
}
