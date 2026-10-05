LIB=lib
help:
	@echo "A default Python module Makefile"

requirements: 
	make install -C $(LIB)
	@uv pip freeze > requirements

install: requirements
	make install -C $(LIB)
	@uv pip install -r requirements
