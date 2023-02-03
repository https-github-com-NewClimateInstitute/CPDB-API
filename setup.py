import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="cpdb-api-dackow",
    version="0.0.1",
    author="Kevin Dackow",
    author_email="kjdackow@gmail.com",
    description="A library to query the Climate Policy Database",
    url="https://github.com/KevinDackow/CPDB-API",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
)
