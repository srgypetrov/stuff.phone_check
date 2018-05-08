all: registry bottle rust

registry:
	python registry/get_registry.py

bottle:
	curl -o web/bottle.py https://raw.githubusercontent.com/bottlepy/bottle/0.12.13/bottle.py

rust:
	cargo build --manifest-path rust/Cargo.toml --release

.PHONY: all registry bottle rust
