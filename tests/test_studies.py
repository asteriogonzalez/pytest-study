import pytest
import time

# make some 'alias'
study = pytest.mark.study
pre = pytest.mark.pre

# You can put the regular tests and the studies in any order
# pytest-study will reorder later


def test_independent():
    "A regular isolated test"
    time.sleep(0.05)

# test marked as study will not be executed unless pass --runstudy
# in command line


@pre(name='AI')
def test_foo():
    "This is a prerequisite test that belongs to the 'AI' study"
    time.sleep(0.1)
    print "Inside foo test!"
    assert True


@pre(name='AI', order=5)
def test_gather_info():
    "Another prerequisite for 'AI' study"
    time.sleep(0.1)


@study(name='AI')
def test_study_one():
    """This is a long computation study that will be executed
    only if test_gather_info() and test_foo() has been passed (in that order)
    """
    time.sleep(0.2)
    print "Study 1 Hello World!"


@pre
def test_bar():
    "This is a prerequisite test belonging to 'default' study"
    time.sleep(0.15)
    print "Inside bar test!"
    assert True


@pre(order=5)
def test_prior_bar():
    "This is the prerequisite that is executed prior test_bar()"
    time.sleep(0.15)


@study(order=1)
def test_study_two():
    """This studio will be executed before test_study_one because
    we have changed the order. All test_study_two() prerequisite will
    be executed before calling, but not test_study_one() prerequisites.

    This allows to execute the studies ASAP.
    """
    time.sleep(0.3)
    print "Study 2 Hello World again!"


@pre('nonkeyword_name')
def test_nonkeyword_name_1():
    pass

@pre('nonkeyword_name')
def test_nonkeyword_name_2():
    pass

@study('nonkeyword_name')
def test_nonkeyword_study():
    pass

