from pulumi import ComponentResource, ResourceOptions

__resource = ComponentResource("data:resource:root", "root")
child_opts = ResourceOptions(parent=__resource)
