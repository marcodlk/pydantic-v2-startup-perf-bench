
.PHONY: benchmark
benchmark:  ## Run the benchmark
	uv run nox -s benchmark


.PHONY: test
test:  ## Run the tests
	uv run nox -s test


.PHONY: help
help:  ## Display this help
	awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m<target>\033[0m\n"} /^[a-zA-Z0-9_-]+:.*?##/ { printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)
