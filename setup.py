import pathlib
from setuptools import setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

setup(
    name="torn_open",
    version="0.0.3",
    python_requires=">=3.6.*",
    description="Tornado x OpenAPI x Redoc",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/b34nst4lk/tornopen/",
    author="Jack Sim",
    license="MIT",
    packages=["torn_open", "torn_open/api_spec"],
    include_package_data=True,
    setup_requires=[
        "wheel",
    ],
    install_requires=[
        "apispec",
        "pydantic",
        "tornado",
        "typed-ast;python_version>='3.8'",
    ],
)
