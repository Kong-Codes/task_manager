.PHONY: create-api-image
create-api-image:
	docker compose up --build

.PHONY: push-dockerhub
push-dockerhub:
	docker tag postgres:15 kongcodes/task_manager_db:0.1.0
	docker push kongcodes/task_manager_db:0.1.0

	docker tag task_manager-web kongcodes/task_manager_api:0.1.0
	docker push kongcodes/task_manager_api:0.1.0