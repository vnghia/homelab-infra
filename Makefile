reset-db:
	pulumi up --replace 'urn:pulumi:prod::homelab-infra::data:resource:root$$data:docker:Volume$$docker:index/volume:Volume::${type}-${service}-data-prod' -y
