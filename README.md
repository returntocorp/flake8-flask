# Flake8 plugin for Flask, by r2c

Flake8 plugin for detecting flask best practices

## Checks

## Installing

```
$ python -m pip install flake8-flask
```

_Specify `python2` or `python3` to install for a specific Python version._

And double check that it was installed correctly:

```
$ python -m flake8 -h
Usage: flake8 [options] file file ...

...

Installed plugins: flake8-flask8: 0.0.1, mccabe: 0.5.3, pycodestyle: 2.2.0, pyflakes: 1.3.0
```

## Using

Click best practices is a flake8 plugin. You can easily use this plugin by

```
$ python -m flake8 --select=R2C /path/to/code
```

## Testing

```
$ pytest
```
