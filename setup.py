from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand
from setuptools.command.install_scripts import install_scripts
from setuptools.command.install import install as _install
from os.path import join as pjoin, splitext, split as psplit
import sys
import os


INSTALLATION_ERROR = """INSTALLATION ERROR!

BiblioPixel v3 requires Python 3.4+ but
you are using version {0.major}.{0.minor}.{0.micro}

If you absolutely require using Python 2,
please install BiblioPixel v2.x using:

    > pip install "bibliopixel<3.0"

However we highly recommend using the latest BiblioPixel
(v3+) with Python 3.4+.
"""


BAT_TEMPLATE = \
    r"""@echo off
REM wrapper to use shebang first line of {FNAME}
set mypath=%~dp0
set pyscript="%mypath%{FNAME}"
set /p line1=<%pyscript%
if "%line1:~0,2%" == "#!" (goto :goodstart)
echo First line of %pyscript% does not start with "#!"
exit /b 1
:goodstart
set py_exe=%line1:~2%
call "%py_exe%" %pyscript% %*
"""


class do_install_scripts(install_scripts):

    def run(self):
        install_scripts.run(self)
        if not os.name == "nt":
            return
        for filepath in self.get_outputs():
            # If we can find an executable name in the #! top line of the script
            # file, make .bat wrapper for script.
            with open(filepath, 'rt') as fobj:
                first_line = fobj.readline()
            if not (first_line.startswith('#!') and
                    'python' in first_line.lower()):
                print("No #!python executable found, skipping .bat wrapper")
                continue
            pth, fname = psplit(filepath)
            froot, ext = splitext(fname)
            bat_file = pjoin(pth, froot + '.bat')
            bat_contents = BAT_TEMPLATE.replace('{FNAME}', fname)
            print("Making %s wrapper for %s" % (bat_file, filepath))
            if self.dry_run:
                continue
            with open(bat_file, 'wt') as fobj:
                fobj.write(bat_contents)


if sys.version_info.major != 3:
    print(INSTALLATION_ERROR.format(sys.version_info))
    sys.exit(1)


# From here: http://pytest.org/2.2.4/goodpractises.html
class RunTests(TestCommand):
    DIRECTORY = 'test'

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = [self.DIRECTORY]
        self.test_suite = True

    def run_tests(self):
        # Import here, because outside the eggs aren't loaded.
        import pytest
        errno = pytest.main(self.test_args)
        if errno:
            raise SystemExit(errno)


class RunBenchmark(RunTests):
    DIRECTORY = 'benchmark'


class RunCoverage(RunTests):
    def run_tests(self):
        import coverage
        cov = coverage.Coverage(config_file=True)

        cov.start()
        super().run_tests()
        cov.stop()

        cov.report(file=sys.stdout)
        coverage = cov.html_report(directory='htmlcov')
        fail_under = cov.get_option('report:fail_under')
        if coverage < fail_under:
            print('ERROR: coverage %.2f%% was less than fail_under=%s%%' % (
                  coverage, fail_under))
            raise SystemExit(1)


def _get_version():
    from os.path import abspath, dirname, join
    filename = join(dirname(abspath(__file__)), 'bibliopixel', 'VERSION')
    return open(filename).read().strip()


VERSION = _get_version()

with open('requirements.txt') as f:
    REQUIRED = f.read().splitlines()

setup(
    name='BiblioPixel',
    version=VERSION,
    description=(
        'BiblioPixel is a pure python library for manipulating a wide variety '
        'of LED strip based displays, both in strip and matrix form.'),
    author='Adam Haile',
    author_email='adam@maniacallabs.com',
    url='http://github.com/maniacallabs/bibliopixel/',
    license='MIT',
    packages=find_packages(exclude=['test']) + ['ui', 'scripts'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    tests_require=['pytest'],
    cmdclass={
        'benchmark': RunBenchmark,
        'coverage': RunCoverage,
        'test': RunTests,
        'install_scripts': do_install_scripts
    },
    include_package_data=True,
    scripts=['scripts/bibliopixel'],
    install_requires=REQUIRED
)
