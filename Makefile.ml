# ML convenience targets (alongside space.mk)

PY ?= python

.PHONY: ml-test
ml-test:
	$(PY) -m pytest -q tests -m "not slow" --cov=src --cov-report=term --cov-report=xml

.PHONY: ml-cli
ml-cli:
	$(PY) -m src.codex_ml.experiments.cli list --limit 5 || true

.PHONY: ds-validate
ds-validate:
	@if [ -z "$(path)" ]; then echo "Usage: make ds-validate path=<file>"; exit 2; fi
	$(PY) -m src.codex_ml.data.cli validate $(path)

.PHONY: ds-metadata
ds-metadata:
	@if [ -z "$(path)" ]; then echo "Usage: make ds-metadata path=<file>"; exit 2; fi
	$(PY) -m src.codex_ml.data.cli metadata $(path)

.PHONY: docker-build-cpu
docker-build-cpu:
	docker build -t codex-ml:cpu -f Dockerfile .

.PHONY: docker-build-gpu
docker-build-gpu:
	docker build -t codex-ml:gpu -f Dockerfile.gpu .

.PHONY: k8s-apply
k8s-apply:
	kubectl apply -f deploy/kubernetes/configmap.yaml
	kubectl apply -f deploy/kubernetes/deployment.yaml
