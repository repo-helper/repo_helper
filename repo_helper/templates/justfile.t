default: lint

pdf-docs: latex-docs
	make -C doc-source/build/latex/

latex-docs:
	SPHINX_BUILDER=latex tox -e docs
{% if enable_qa %}
unused-imports:
	tox -e lint -- --select F401

incomplete-defs:
	tox -e lint -- --select MAN
{% endif %}
vdiff:
	git diff $(repo-helper show version -q)..HEAD

bare-ignore:
	greppy '# type:? *ignore(?!\[|\w)' -s

lint: {% if enable_qa %}unused-imports incomplete-defs{% endif %} bare-ignore
	{% if enable_qa %}tox -n qa{% endif %}
