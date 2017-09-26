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

## Usage

The following parameters are available from the command line


```bash
$ pytest --help

... (other options are not shown) ...

custom options:
  --show_order          show tests and studies order execution and which are
                        selected for execution.
  --runstudy=all|reg expression
                        regular expression for the studies names ('all' runs
                        all). None is selected by default.
```

Executing pytest showing the hooks trace  would yield something like;

```bash
$ pytest --duration=10 --show_order
====================================== test session starts =======================================
platform linux2 -- Python 2.7.13, pytest-3.2.2, py-1.4.34, pluggy-0.4.0
plugins: study-0.12, timeout-1.2.0, testmon-0.9.6, race-0.1.1, pep8-1.0.6, cov-2.5.1, colordots-0.1, dependency-0.2
collected 3 items                                                                                 
+  0 [       ] tests/test_studies.py:test_independent
-  1 [default] tests/test_studies.py:test_foo
-  2 [default] tests/test_studies.py:test_study_one

tests/test_studies.py .

=================================== slowest 10 test durations ====================================
0.05s call     tests/test_studies.py::test_independent
0.00s setup    tests/test_studies.py::test_independent
0.00s teardown tests/test_studies.py::test_independent
==================================== 1 passed in 0.08 seconds ====================================

```

where only `test_indepent()` has been called (note the `call` tag) and the others are skipped from execution.

Now, executing pytest with `--runstudy=all` we get show:

```bash
$ pytest --duration=10 --show_order --runstudy=all
====================================== test session starts =======================================
platform linux2 -- Python 2.7.13, pytest-3.2.2, py-1.4.34, pluggy-0.4.0
plugins: study-0.12, timeout-1.2.0, testmon-0.9.6, race-0.1.1, pep8-1.0.6, cov-2.5.1, colordots-0.1, dependency-0.2
collected 3 items                                                                                 
+  0 [       ] tests/test_studies.py:test_independent
+  1 [default] tests/test_studies.py:test_foo
+  2 [default] tests/test_studies.py:test_study_one

tests/test_studies.py ...

=================================== slowest 10 test durations ====================================
0.20s call     tests/test_studies.py::test_study_one
0.10s call     tests/test_studies.py::test_foo
0.05s call     tests/test_studies.py::test_independent
0.00s setup    tests/test_studies.py::test_independent
0.00s teardown tests/test_studies.py::test_independent
0.00s setup    tests/test_studies.py::test_foo
0.00s setup    tests/test_studies.py::test_study_one
0.00s teardown tests/test_studies.py::test_foo
0.00s teardown tests/test_studies.py::test_study_one
==================================== 3 passed in 0.38 seconds ====================================


```

where `test_foo()` and `test_study_one()` has been called as well.
Note the `+` symbol at the beginning of each test shown by `--show_order` option.


## Studies interdependences

We can add more test studies and group them by name and setting a relative priority for the studies executions with the keyword `order=<value>`. The default priority is 1000, so any value lower will be executed first and the reverse is also true.

All prerequisites belonging to the same study with be ordered using the same criteria.

Let's create a more rich example with a group named 'AI' and set some execution order:

```python
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

```

If we execute pytest with the `--show_order` option as well, the output would be similar to:

```bash
$ pytest --duration=10 --show_order 
====================================== test session starts =======================================
platform linux2 -- Python 2.7.13, pytest-3.2.2, py-1.4.34, pluggy-0.4.0
plugins: study-0.12, timeout-1.2.0, testmon-0.9.6, race-0.1.1, pep8-1.0.6, cov-2.5.1, colordots-0.1, dependency-0.2
collected 7 items                                                                                 
+  0 [       ] tests/test_studies.py:test_independent
-  1 [default] tests/test_studies.py:test_prior_bar
-  2 [default] tests/test_studies.py:test_bar
-  3 [default] tests/test_studies.py:test_study_two
-  4 [     AI] tests/test_studies.py:test_gather_info
-  5 [     AI] tests/test_studies.py:test_foo
-  6 [     AI] tests/test_studies.py:test_study_one

tests/test_studies.py .

=================================== slowest 10 test durations ====================================
0.05s call     tests/test_studies.py::test_independent
0.00s setup    tests/test_studies.py::test_independent
0.00s teardown tests/test_studies.py::test_independent
==================================== 1 passed in 0.08 seconds ====================================

```

where the sequence order, the selected flag and the name of associate study is show for each test.

To run a one or more studies we can use a regular expression that match the studio name.

```bash
$ pytest --duration=10 --show_order --runstudy='AI'
====================================== test session starts =======================================
platform linux2 -- Python 2.7.13, pytest-3.2.2, py-1.4.34, pluggy-0.4.0
plugins: study-0.12, timeout-1.2.0, testmon-0.9.6, race-0.1.1, pep8-1.0.6, cov-2.5.1, colordots-0.1, dependency-0.2
collected 7 items                                                                                 
+  0 [       ] tests/test_studies.py:test_independent
+  1 [     AI] tests/test_studies.py:test_gather_info
+  2 [     AI] tests/test_studies.py:test_foo
+  3 [     AI] tests/test_studies.py:test_study_one
-  4 [default] tests/test_studies.py:test_prior_bar
-  5 [default] tests/test_studies.py:test_bar
-  6 [default] tests/test_studies.py:test_study_two

tests/test_studies.py ....

=================================== slowest 10 test durations ====================================
0.20s call     tests/test_studies.py::test_study_one
0.10s call     tests/test_studies.py::test_foo
0.10s call     tests/test_studies.py::test_gather_info
0.05s call     tests/test_studies.py::test_independent
0.00s setup    tests/test_studies.py::test_independent
0.00s setup    tests/test_studies.py::test_gather_info
0.00s setup    tests/test_studies.py::test_study_one
0.00s setup    tests/test_studies.py::test_foo
0.00s teardown tests/test_studies.py::test_foo
0.00s teardown tests/test_studies.py::test_independent
==================================== 4 passed in 0.48 seconds ====================================
```


## Install

```
$ pip install pytest-study
```

or download and improve the code by yourself :) installing in develop mode in your home directory

```
 python setup.py develop --user
```


## Python versions

Is tested only in python 2.7 yet, but there is not any deliberated incompatibility with python 3.x versions.
