from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in zebra/__init__.py
from zebra import __version__ as version

setup(
	name="zebra",
	version=version,
	description="zebra",
	author="eusectra",
	author_email="hello@phamos.com",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
