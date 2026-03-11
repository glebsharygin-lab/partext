.PHONY: test help clean

INPUT ?= vimsika
OUTPUT ?= output

help:
	@echo "Available targets:"
	@echo "  make test [INPUT=folder] [OUTPUT=folder]  - Run publish script"
	@echo "  make clean                                  - Remove output folder"
	@echo ""
	@echo "Examples:"
	@echo "  make test"
	@echo "  make test INPUT=jsons"
	@echo "  make test INPUT=jsons OUTPUT=build"

test:
	python3 scripts/publish.py $(INPUT) $(OUTPUT)

clean:
	rm -rf $(OUTPUT)

.DEFAULT_GOAL := help
