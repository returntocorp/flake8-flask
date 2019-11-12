import setuptools

requires = ["flake8 > 3.6.0"]

with open("README.md") as fin:
    long_description = fin.read()

setuptools.setup(
    name="flake8_flask",
    version="0.1.2",
    description="flake8 plugin with checks for the Flask framework, by r2c",
    long_description=long_description,
    long_description_content_type='text/markdown',
    author="grayson",
    author_email="grayson@r2c.dev",
    url="https://r2c.dev",
    package_dir={"": "src/"},
    packages=["flake8_flask"],
    python_requires=">=3.6",
    entry_points={
        "flake8.extension": [
            "R2C202=flake8_flask.send_file_checks:SendFileChecks",
            "R2C203=flake8_flask.secure_set_cookies:SecureSetCookies",
            "R2C204=flake8_flask.talisman_checks:TalismanChecks",
        ],
    },
    classifiers=[
        "Framework :: Flake8",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Topic :: Software Development :: Quality Assurance"
    ],
)
