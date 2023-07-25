from pulumi import ComponentResource, ResourceOptions

__resource = ComponentResource("service:resource:root", "root")
child_opts = ResourceOptions(parent=__resource)
