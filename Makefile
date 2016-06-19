.PHONY: tests

tests: clean
	@nosetests -sv ./tests/
clean:
	find . -name '*.pyc' | xargs rm -f
