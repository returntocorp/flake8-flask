import setuptools

requires = ["flake8 > 3.6.0"]

setuptools.setup(
    name='flake8_flask',
    version='0.0.5',
    description='r2c checks for flask',
    author='grayson',
    author_email='grayson@r2c.dev',
    url="https://github.com/returntocorp/flake8-flask",
    package_dir={'': 'src/'},
    packages=['flake8_flask'],
    entry_points={
        'flake8.extension': [
            'R2C202=flake8_flask.send_file_checks:SendFileChecks',
        ],
    },
    classifiers=[
        "Framework :: Flake8",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
    ]
)
