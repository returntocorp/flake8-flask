import json
import setuptools

# Version management
with open("VERSION", 'r') as fin:
    __version__ = fin.read().strip()
with open("analyzer.json", 'r') as fin:
    analyzer_json = json.load(fin)
analyzer_json['version'] = __version__
with open("analyzer.json", 'w') as fout:
    json.dump(analyzer_json, fout)

requires = ["flake8 > 3.6.0"]

with open("README.md") as fin:
    long_description = fin.read()

setuptools.setup(
    name="flake8_flask",
    version=__version__,
    description="flake8 plugin with checks for the Flask framework, by r2c",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="grayson",
    author_email="grayson@r2c.dev",
    url="https://r2c.dev",
    package_dir={"": "src/"},
    packages=["flake8_flask"],
    python_requires=">=3.6",
    entry_points={"flake8.extension": ["r2c=flake8_flask.main:Flake8Flask"],},
    classifiers=[
        "Framework :: Flake8",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Topic :: Software Development :: Quality Assurance",
    ],
)
