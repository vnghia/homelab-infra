from pulumi import ComponentResource, ResourceOptions

from _common import constant

__resource = ComponentResource("secret:resource:root", "root")
child_opts = ResourceOptions(parent=__resource, protect=constant.PROJECT_STACK != "dev")
