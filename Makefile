reset-db:
	pulumi up --replace 'urn:pulumi:prod::homelab-infra::data:resource:root$$data:docker:Volume$$docker:index/volume:Volume::${type}-${service}-data-prod' -y
reset-rclone-plugin:
	docker rm -f $$(docker ps -qf 'name=storage-prod$$')
	docker rm -f $$(docker ps -a -qf status=exited)
	pulumi state delete 'urn:pulumi:prod::homelab-infra::data:resource:root$$data:docker:Volume$$data:rclone:root$$docker:index/plugin:Plugin::rclone-volume-plugin-prod' --target-dependents --yes
	pulumi up --yes
reset-restic-init:
	pulumi up --replace 'urn:pulumi:prod::homelab-infra::data:resource:root$$data:backup:Restic$$command:local:Command::restic-repo-init' --yes
