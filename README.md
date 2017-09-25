# pytest-study
A pytest plugin for organizing long run tests (named *studies*) without interfering the regular tests

## Abstract

In situations where we are developing an application or library that will be use to create long computation reports or results, we want to execute the long process only when all the project tests are passed.

`pytest` provide a great support for creating test suits, parallel execution, reports, command line, IDE of CI integration, and so forth, so the idea is to write these long computation code in test from, group them in *studios* and extend pytest with a plugin that allow us to:

- Ignore these long computation *studies* and run only the regular ones.
- Sort all the involved tests so the *study* will be executed only when dependences are passed.
- Define the *studies* and dependences in a easy way.
- Don't interfere with normal pytest use.

## Show me an example

Let' say that we have this `test_studies.py` file:

```python
import pytest
import time

# You can put the regular tests and the studies in any order
# pytest-study will reorder later

def test_independent():
    "A regular isolated test"
    time.sleep(0.05)

# test marked as study will not be executed unless pass --runstudy
# in command line

@pytest.mark.study
def test_foo():
    "This is a test that belongs to the default study"
    time.sleep(0.1)
    print "Inside foo test!"
    assert True

@pytest.mark.study
def test_study_one():
    """This is a long run computation test that will be executed
    only if any previous test has been passed.
    """
    time.sleep(0.2)
    print "Study 1 Hello World!"

```

Executing pytest showing the hooks trace  would yield something like;

```bash
$ pytest --duration=10
============================= test session starts ==============================
platform linux2 -- Python 2.7.13, pytest-3.2.2, py-1.4.34, pluggy-0.4.0
plugins: timeout-1.2.0, testmon-0.9.6, race-0.1.1, pep8-1.0.6, cov-2.5.1, colordots-0.1, dependency-0.2, study-0.1
collected 3 items

tests/test_studies.py .ss

========================== slowest 10 test durations ===========================
0.05s call     tests/test_studies.py::test_independent
0.00s teardown tests/test_studies.py::test_independent
0.00s setup    tests/test_studies.py::test_foo
0.00s setup    tests/test_studies.py::test_study_one
0.00s setup    tests/test_studies.py::test_independent
0.00s teardown tests/test_studies.py::test_study_one
0.00s teardown tests/test_studies.py::test_foo
===================== 1 passed, 2 skipped in 0.07 seconds ======================
```

where only `test_indepent()` has been called (note the mark `call`) and the others are skipped from execution.

Now, executing pytest with `--runstudy` will show:

```bash
$ pytest --duration=10 --runstudy
============================= test session starts ==============================
platform linux2 -- Python 2.7.13, pytest-3.2.2, py-1.4.34, pluggy-0.4.0
plugins: timeout-1.2.0, testmon-0.9.6, race-0.1.1, pep8-1.0.6, cov-2.5.1, colordots-0.1, dependency-0.2, study-0.1
collected 3 items

tests/test_studies.py ...

========================== slowest 10 test durations ===========================
0.20s call     tests/test_studies.py::test_study_one
0.10s call     tests/test_studies.py::test_foo
0.05s call     tests/test_studies.py::test_independent
0.00s setup    tests/test_studies.py::test_foo
0.00s teardown tests/test_studies.py::test_foo
0.00s teardown tests/test_studies.py::test_independent
0.00s setup    tests/test_studies.py::test_study_one
0.00s teardown tests/test_studies.py::test_study_one
0.00s setup    tests/test_studies.py::test_independent
=========================== 3 passed in 0.37 seconds ===========================

```

where `test_foo()` and `test_study_one()` has been called as well.


## Studies interdependences

We can add more test studies and group them by name and setting a relative priority for the studies executions with the keyword `order=<value>`. The default priority is 1000, so any value lower will be executed first and the reverse is also true.

All prerequisites belonging to the same study with be ordered using the same criteria.

Let's create a group named 'AI' and setting some orders:

```python
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
    """This studio will be executed before test_study_one() because
    we have changed the priority order to 1.

    All test_study_two() prerequisites will be executed before calling it
    but none from test_study_one() prerequisites.

    This allows to execute the studies ASAP in blocks.
    """
    time.sleep(0.3)
    print "Study 2 Hello World again!"

```


If we execute pytest with the `--debug` option as well, the output would be similar to:

```bash
$ pytest  --runstudy --debug
============================= test session starts ==============================
platform linux2 -- Python 2.7.13, pytest-3.2.2, py-1.4.34, pluggy-0.4.0 -- /usr/lib/wingide6/wingdb
using: pytest-3.2.2 pylib-1.4.34
collected 7 items
  0 [       ] tests/test_studies.py:test_independent
  1 [default] tests/test_studies.py:test_prior_bar
  2 [default] tests/test_studies.py:test_bar
  3 [default] tests/test_studies.py:test_study_two
  4 [     AI] tests/test_studies.py:test_gather_info
  5 [     AI] tests/test_studies.py:test_foo
  6 [     AI] tests/test_studies.py:test_study_one

tests/test_studies.py .......

=========================== 7 passed in 1.09 seconds ===========================

```

where the sequence order and the name of associate study is show for each test.

## Install

```
$ pip install pytest-study
```

## Python versions

Is tested only in python 2.7, but there is not any deliberated incompatibility with python 3.x versions.
