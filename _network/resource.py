from pulumi import ComponentResource, ResourceOptions

__resource = ComponentResource("network:resource:root", "root")
child_opts = ResourceOptions(parent=__resource)
