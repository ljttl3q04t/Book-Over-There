deploy:
	cd deploy && ansible-playbook -i hosts deploy.yml

.PHONY: deploy
