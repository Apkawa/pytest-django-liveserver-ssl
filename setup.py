# !/usr/bin/env python
import os
import sys

from setuptools import setup, find_packages

version = "0.0.2"

if sys.argv[-1] == "publish":
    # For initial publishing
    try:
        import wheel

        print("Wheel version: ", wheel.__version__)
    except ImportError:
        print('Wheel library missing. Please run "pip install wheel"')
        sys.exit()
    os.system("rm -rf dist/")
    os.system("python setup.py sdist bdist_wheel")
    os.system("twine upload dist/*")
    sys.exit()

if sys.argv[1] == "bumpversion":
    print("bumpversion")
    try:
        part = sys.argv[2]
    except IndexError:
        part = "patch"

    os.system("bump2version --config-file setup.cfg %s" % part)
    sys.exit()

__doc__ = ""

project_name = "pytest-django-liveserver-ssl"
app_name = "pytest_django_liveserver_ssl"

ROOT = os.path.dirname(__file__)


def read(fname):
    return open(os.path.join(ROOT, fname)).read()


setup(
    name=project_name,
    version=version,
    description=__doc__,
    long_description=read("README.md"),
    long_description_content_type="text/markdown",
    url="https://github.com/Apkawa/%s" % project_name,
    author="Apkawa",
    author_email="apkawa@gmail.com",
    packages=[package for package in find_packages() if package.startswith(app_name)],
    entry_points={
        "pytest11": ["django_liveserver_ssl = pytest_django_liveserver_ssl.plugin"]
    },
    python_requires=">=3.7, <4",
    install_requires=["Django", "pytest-django", "pyopenssl", "typing-extensions"],
    zip_safe=False,
    include_package_data=True,
    keywords=[],
    license="MIT",
    classifiers=[
        # https://pypi.org/classifiers/
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Environment :: Web Environment",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        # 'Programming Language :: Python :: Implementation :: PyPy',
    ],
)
