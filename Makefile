all: registry rust

registry:
	python registry/get_registry.py

rust:
	cargo build --manifest-path rust/Cargo.toml --release

.PHONY: all registry rust
