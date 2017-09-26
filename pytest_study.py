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
try:
    import wingdbstub
except ImportError:
    pass

import re
import pytest
from blessings import Terminal

term = Terminal()

MARKS = ['study', 'pre']  # match 1st ocurrence


def parse_args(args, kwargs):
    "update kwargs with positional arguments"
    positional = ['name', 'order']
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


def get_FQN(item):
    "Get the Full Qualified Name of a test item"
    names = []
    for x in item.listchain():
        if not isinstance(x, (pytest.Session, pytest.Instance)):
            names.append(x.name)

    return ':'.join(names)

# ------------------------------------------
# Skip studio tests
# ------------------------------------------


def pytest_addoption(parser):
    "Add the --runstudy option in command line"
    # parser.addoption("--runstudy", action="store_true",
                    # default=False, help="run studio processes")

    parser.addoption("--show_order", action="store_true",
                    default=False,
                    help="""show tests and studies order execution
                    and which are selected for execution.""")

    parser.addoption("--runstudy", action="store", type="string",
                    default='', metavar='all|reg expression',
                    help="""regular expression for the studies names
                    ('all' runs all).
                    None is selected by default.""")


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
    run_study = config.getoption("--runstudy")
    # 'all' will match all studies, '' will not match anything
    run_study = {'': '(?!x)x', 'all': '.*'}.get(run_study, run_study)
    # --runstudy given in cli: do not skip study tests and
    test_selected = list()
    test_skipped = list()
    groups = dict()
    incremental = pytest.mark.incremental()

    def add():
        "helper for gathering test info"
        marker = item.get_marker(mark)
        kwargs = parse_args(marker.args, marker.kwargs)
        group_name = kwargs['name']
        group = groups.setdefault(group_name, dict())
        group.setdefault(mark, list()).append((kwargs, item))
        item.add_marker(incremental)

    # place every test in regular, prerequisite and studies
    # group by name
    for item in items:
        for mark in set(item.keywords.keys()).intersection(MARKS):
            add()
            break
        else:
            test_selected.append(item)

    def sort(a, b):
        "Sort two items by order priority"
        return cmp(a[0]['order'], b[0]['order'])

    # use studies precedence to built the global sequence order
    mandatory = 'study'  # mandatory mark for global sorting: study
    studies = list()
    for name, info in groups.items():
        studies.extend(info.get(mandatory, []))
    studies.sort(sort)

    def append(tests, where):
        "helper to add the test item from info structure"
        for test in tests:
            test = test[1]
            if test not in where:
                where.append(test)

    # select only the test that are going to be launched
    width = 0
    regexp = re.compile(run_study, re.I | re.DOTALL)
    for study in studies:
        group_name = study[0]['name']
        width = max(width, len(group_name))
        where = test_selected if regexp.search(group_name) else test_skipped
        for mark, seq in groups[group_name].items():
            if mark == mandatory:
                continue
            seq.sort(sort)
            append(seq, where)
        append([study], where)

    if config.getoption("--show_order") or config.getoption("--debug"):
        fmt = "{0:>3d} [{1:>%s}] {2}" % width
        for i, item in enumerate(test_selected + test_skipped):
            study = get_study_name(item)
            fqn = get_FQN(item)
            line = fmt.format(i, study, fqn)
            if item in test_selected:
                line = term.green('+' + line)
            else:
                line = term.yellow('-' + line)
            print(line)

    # we make the --runstudy check at the end to be able to show
    # test order with --show_order or --debig options
    # reorder tests by group name and replace items IN-PLACE
    if run_study:
        items[:] = test_selected
        return

    skip_test = pytest.mark.skip(reason="need --runstudy option to run")
    for item in items:
        if set(item.keywords.keys()).intersection(MARKS):
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
