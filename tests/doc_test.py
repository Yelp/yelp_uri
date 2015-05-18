from __future__ import print_function


def test_docs():
    from doctest import testfile
    failures, _ = testfile('README.md', module_relative=False, encoding='UTF-8')
    assert not failures
