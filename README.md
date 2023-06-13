Pud
===

![PyPI](https://img.shields.io/pypi/v/pud)


Pud is a mini command-line tool to navigate directories.

Installation
===
PIP:
```
pip install pud
```

GIT (Dev Version):
```
git clone https://github.com/Jedddy/pud.git

python setup.py install
```

Usage
===
```
pud [arguments]
```

Shortcuts
===
```
[?] - Show help
[ctrl + i] - Show file or folder info
```

Options
===
Currently there are 2 options:
- cursor: The cursor you want to use.
    ```
    pud --cursor=">>>"
    ```
- no-keep-state: Whether not to keep the state of your cursor after entering/leaving a directory
    ```
    pud --no-keep-state
    ```
