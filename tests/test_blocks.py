from git_helper.blocks import installation_regex, short_desc_regex, links_regex, shields_regex
import lorem  # type: ignore
import pytest  # type: ignore


@pytest.mark.parametrize("value", [
		".. start installation\n\n..end installation",
		f".. start installation\n{lorem.paragraph()}\n..end installation"
		])
def test_installation_regex(value):
	m = installation_regex.sub(value, "hello world")
	assert m == "hello world"


@pytest.mark.parametrize("value", [
		".. start links\n\n..end links",
		f".. start links\n{lorem.paragraph()}\n..end links"
		])
def test_links_regex(value):
	m = links_regex.sub(value, "hello world")
	assert m == "hello world"


@pytest.mark.parametrize("value", [
		".. start shields\n\n..end shields",
		f".. start shields\n{lorem.paragraph()}\n..end shields"
		])
def test_shields_regex(value):
	m = shields_regex.sub(value, "hello world")
	assert m == "hello world"


@pytest.mark.parametrize("value", [
		".. start short_desc\n\n..end short_desc",
		f".. start short_desc\n{lorem.paragraph()}\n..end short_desc"
		])
def test_short_desc_regex(value):
	m = short_desc_regex.sub(value, "hello world")
	assert m == "hello world"
