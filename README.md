<a href="https://waffle.io/Javyre/systhemer"><img src="https://badge.waffle.io/Javyre/systhemer2.png?label=ready&title=Ready" alt="Waffle.io"></a>

<p align="center"><img src="https://github.com/Javyre/systhemer2/raw/master/assets/SysthemerLogoNoCircle.png" alt="Systhemer"/></p>

***

<p align="center">
<b><a href="http://systhemer2.readthedocs.io">API Documentation</a></b>
|
<b><a href="https://github.com/Javyre/systhemer2/wiki">User Documentation</a></b>
</p>

***

# systhemer2
A system theming utility designed for ease of sharing

## What is this?
Systhemer is a system theming utility that is designed to be easily
extended for support for new programs by the community and for ease
of sharing of user themes.

Our goal is to make sharing system configurations to others easier than
ever: just apply your `{theme-name}.toml` and BAM you're done!

## Usage
Here's what `systhemer -h` will tell you:
```
usage: systhemer [-h] [-v] [-nc] path

Systhemer: System themingutility designed for ease of sharing

positional arguments:
  path                path to theme file

optional arguments:
  -h, --help          show this help message and exit
  -v, --verbose       set level of verbosity
  -nc, --no-colorlog  disable colorlog

```

Just run the program with the path to the theme to be apppied as the argument and you're done!

## Development Status:
Systhemer is in early development and doesn't yet include all the feature that are planned for it.

Here's some of what we have in plan for it in the future:

| Feature | Status |
|---------|--------|
| Backup existing config | In Progress |
| Support for XML | Not Started |
| OpenBox support | Not Started |
| Xresources support | Not Started |
| bspwm support | Not Started |
| rofi support | Not Started |
