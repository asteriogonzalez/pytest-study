import pytest
import time

# You can put the regular tests and the studies in any order
# pytest-study will reorder later


def test_independent():
    "A regular isolated test"
    time.sleep(0.05)

# test marked as study will not be executed unless pass --runstudy
# in command line


@pytest.mark.pre(name='AI')
def test_foo():
    "This is a prerequisite test that belongs to the 'AI' study"
    time.sleep(0.1)
    print "Inside foo test!"
    assert True


@pytest.mark.pre(name='AI', order=5)
def test_gather_info():
    "Another prerequisite for 'AI' study"
    time.sleep(0.1)


@pytest.mark.study(name='AI')
def test_study_one():
    """This is a long computation study that will be executed
    only if test_gather_info() and test_foo() has been passed (in that order)
    """
    time.sleep(0.2)
    print "Study 1 Hello World!"


@pytest.mark.pre
def test_bar():
    "This is a prerequisite test belonging to 'default' study"
    time.sleep(0.15)
    print "Inside bar test!"
    assert True


@pytest.mark.pre(order=5)
def test_prior_bar():
    "This is the prerequisite that is executed prior test_bar()"
    time.sleep(0.15)


@pytest.mark.study(order=1)
def test_study_two():
    """This studio will be executed before test_study_one because
    we have changed the order. All test_study_two() prerequisite will
    be executed before calling, but not test_study_one() prerequisites.

    This allows to execute the studies ASAP.
    """
    time.sleep(0.3)
    print "Study 2 Hello World again!"
