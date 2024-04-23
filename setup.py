from setuptools import setup, find_packages


def readfile(path):
    with open(path, "rt") as f:
        return f.read()


setup(
    name="runseq",
    author="Luís Gomes",
    author_email="luismsgomes@gmail.com",
    version="0.0.2",
    description=(readfile("README.md")),
    py_modules=["runseq"],
    package_dir={"": "."},
    install_requires=[],
    packages=find_packages("."),
    include_package_data=False,
    package_data={"": []},
    entry_points={
        "console_scripts": [
            "runseq=runseq:main",
        ]
    },
    url="https://github.com/luismsgomes/runseq"
)
