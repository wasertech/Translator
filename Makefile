.PHONY: 

release:
	@python -m build
	@python -m twine upload dist/*
	@rm dist/*
