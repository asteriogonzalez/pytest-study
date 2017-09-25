"""
In situations where we are developing an application or library
that will be use to create long computation reports or results,
we want to execute the long process only when all the project tests
are passed.

pytest provide a great support for creating test suits,
parallel execution, reports, command line, IDE of CI integration,
and so forth, so the idea is to write these long computation code
in test from, group them in studios and extend pytest with a plugin
that allow us to:

- Ignore these long computation studies and run only the regular ones.
- Sort all the involved tests so the study will be executed only when
  all dependences are passed.
- Define the studies and dependences in a easy way.
- Don't interfere with normal pytest use.

For a more detailed refecences, please read README.md or
visit https://github.com/asteriogonzalez/pytest-study
"""
from __future__ import print_function
# try:
    # import wingdbstub
# except ImportError:
    # pass

import pytest
from blessings import Terminal

term = Terminal()

MARKS = ['study', 'pre']  # match 1st ocurrence


def parse_args(args, kwargs):
    "update kwargs with positional arguments"
    positional = ['name', 'order'],
    kw = {'name': 'default', 'order': 1000}
    kw.update(kwargs)
    for key in kwargs:
        if key in positional:
            positional.remove(key)
    for i, val in enumerate(args):
        kw[positional[i]] = val

    return kw


def get_study_name(item):
    "Try to get the name where the test belongs to, or '' when is free"
    for mark in MARKS:
        marker = item.get_marker(mark)
        if marker:
            return parse_args(marker.args, marker.kwargs)['name']
    return ''

# ------------------------------------------
# Skip studio tests
# ------------------------------------------


def pytest_addoption(parser):
    "Add the --runstudy option in command line"
    parser.addoption("--runstudy", action="store_true",
                     default=False, help="run studio processes")


def pytest_collection_modifyitems(config, items):
    """Remove all study tests if --runstudy is not selected
    and reorder the study dependences to be executed incrementaly
    so any failed study test will abort the complete sequence.

    - Mark a test with @pytest.mark.study to consider part of a study.
    - Mark a test with @pytest.mark.study and named 'test_study_xxxx()'
      to be executed at the end when all previous test study functions
      are passed.
    """
    # check if studio tests myst be skipped
    if config.getoption("--runstudy"):
        # --runstudy given in cli: do not skip study tests and
        # set @pytest.hookimpl(trylast=True) by default for all studio tests
        test_sequence = list()
        groups = dict()
        incremental = pytest.mark.incremental()

        def add():
            "helper for gathering test info"
            marker = item.get_marker(mark)
            kwargs = parse_args(marker.args, marker.kwargs)
            name = kwargs['name']
            group = groups.setdefault(name, dict())
            group.setdefault(mark, list()).append((kwargs, item))
            item.add_marker(incremental)

        # place every test in regular, prerequisite and studies
        # group by name
        for item in items:
            for mark in set(item.keywords.keys()).intersection(MARKS):
                add()
                break
            else:
                test_sequence.append(item)

        def sort(a, b):
            "Sort two items by order priority"
            return cmp(a[0]['order'], b[0]['order'])

        # use studies precedence to built the global sequence order
        mandatory = 'study'  # mandatory mark for global sorting: study
        studies = list()
        for name, info in groups.items():
            studies.extend(info.get(mandatory, []))
        studies.sort(sort)

        def append(tests):
            "helper to add the test item from info structure"
            for test in tests:
                test_sequence.append(test[1])

        width = 0
        for study in studies:
            name = study[0]['name']
            width = max(width, len(name))
            for mark, seq in groups[name].items():
                if mark == mandatory:
                    continue
                seq.sort(sort)
                append(seq)
            append([study])

        # reorder tests by group name and replace items IN-PLACE
        if config.getoption("--debug"):
            fmt = "{0:>3d} [{1:>%s}] {2}" % width
            for i, item in enumerate(test_sequence):
                name = get_study_name(item)
                line = fmt.format(i, name, ':'.join(item.listnames()[-2:]))
                line = term.yellow(line)
                print(line)

        items[:] = test_sequence
        return

    skip_test = pytest.mark.skip(reason="need --runstudy option to run")
    for item in items:
        if "study" in item.keywords:
            item.add_marker(skip_test)

# ------------------------------------------
# incremental failure chain (from pytest doc)
# ------------------------------------------


def pytest_runtest_makereport(item, call):
    "set the last failed test"
    if "incremental" in item.keywords:
        if call.excinfo is not None:
            parent = item.parent
            parent._previousfailed = item


def pytest_runtest_setup(item):
    "Abort the execution stage if a previous incremental test has failed"
    if "incremental" in item.keywords:
        previousfailed = getattr(item.parent, "_previousfailed", None)
        if previousfailed is not None:
            pytest.xfail("previous test failed (%s)" % previousfailed.name)
