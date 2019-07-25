SCHEMAS_DIR=rtf_proxy/schemas
STRUCTS=rtf_proxy/structs/

structs:
	mkdir -p $(STRUCTS)
	kaitai-struct-compiler -t python --outdir $(STRUCTS) $(SCHEMAS_DIR)/*.ksy


venv: requirements.txt
	virtualenv venv
	./venv/bin/pip install -r requirements.txt
	touch venv
