.PHONY: list

list: ## List all available commands
	@echo "Available commands:"
	@echo
	@awk '/^[a-zA-Z_-]+:.*?##/ { \
		helpMessage = match(lastLine, /^## (.*)/); \
		if (helpMessage) { \
			helpCommand = $$1; \
			helpMessage = substr(lastLine, RSTART + 3, RLENGTH); \
			printf "  \033[36m%-30s\033[0m %s\n", helpCommand, helpMessage; \
		} \
	  } \
	{lastLine = $$0}' $(MAKEFILE_LIST)


clean:
	rm -rf logs/*

run_api:
	@echo "Running API"
	@uvicorn main:app --reload
