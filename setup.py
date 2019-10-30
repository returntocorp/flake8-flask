import setuptools

setuptools.setup(
    name='flake8_flask',
    version='0.0.1',
    description='r2c checks for flask',
    author='grayson',
    author_email='grayson@r2c.dev',
    package_dir={'': 'src/'},
    packages=['flake8_flask'],
    entry_points={
        'flake8.extension': [
            'R2C202=flake8_flask.send_file_check:SendFileCheck',
        ],
    },
)
