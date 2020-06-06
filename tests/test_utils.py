# this package
from git_helper.utils import validate_classifiers


def test_errors(capsys):
	validate_classifiers(["Foo :: Bar", "Foo :: Bar :: Baz", 'Fuzzy :: Wuzzy :: Was :: A :: Bear'])
	captured = capsys.readouterr()

	stderr = captured.err.split("\n")
	assert stderr[0].endswith("Unknown Classifier 'Foo :: Bar'!")
	assert stderr[1].endswith("Unknown Classifier 'Foo :: Bar :: Baz'!")
	assert stderr[2].endswith("Unknown Classifier 'Fuzzy :: Wuzzy :: Was :: A :: Bear'!")
	assert not captured.out


def test_deprecated(capsys):
	validate_classifiers(['Natural Language :: Ukranian'])
	captured = capsys.readouterr()

	stderr = captured.err.split("\n")
	assert stderr[0].endswith("Classifier 'Natural Language :: Ukranian' is deprecated!")
	assert not captured.out


def test_valid(capsys):
	validate_classifiers(['Natural Language :: Ukrainian', 'License :: OSI Approved'])
	captured = capsys.readouterr()
	assert not captured.out
	assert not captured.err
