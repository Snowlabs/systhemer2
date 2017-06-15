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
ever: just apply your `{theme-name}.ini` and BAM you're done!

## Usage
Here's what `systhemer -h` will tell you:
```
usage: systhemer [-h] [-i] [-v] [-l] [-d] [-D] [-n] [-b]
                 [--VDEBUG_LVL VDEBUG_LVL] [-f PATH] [-nc] [-nt]
                 [-! EXCLUDED_PROGS]

Systhemer: System themingutility designed for ease of sharing

optional arguments:
  -h, --help            show this help message and exit
  -i, --interactive     run Systhemer in interactive mode
  -v, --verbose         set level of verbosity
  -l, --list            list supported programs
  -d, --diff            generate diff before saving output file
  -D, --alt-diff        alternative diff format (use with --diff)
  -n, --no-save         don't save file (useful for debugging and for use with
                        --diff)
  -b, --mk-backup       save a backup (.bak) file
  --VDEBUG_LVL VDEBUG_LVL
                        set VDEBUG_LVL
  -f PATH, --file PATH  path to theme file
  -nc, --no-colors      disable colors
  -nt, --no-truncate-log
                        disable single-letter verbosity indicators
  -! EXCLUDED_PROGS, --blacklist EXCLUDED_PROGS
                        blacklist of excluded programs (comma separated)
```

Just run the program with `-f` followed by the path to the theme to be applied as the argument and you're done!

## Development Status:
Systhemer is in early development and doesn't yet include all the feature that are planned for it.

Things to do for a proper release, in order of priority starting from highest.

| Feature                                  | Status      |
| ---------------------------------------- | ----------- |
| Implement color formats for config rules | Done!       |
| Restructure project for improved modularity | Not Started |
| Add proper code documentation on RTD     | WIP         |
| Refactor code for readability            | WIP         |
| Backup existing config                   | Done! |
| Support for XML                          | Not Started |

Here are the program definitions which are currently planned for addition.

| Feature    | Status      |
| ---------- | ----------- |
| OpenBox    | Not Started |
| Xresources | Not Started |
| bspwm      | Not Started |
| rofi       | Not Started |

Optional features planned for future versions.

| Feature                                  |
| :--------------------------------------- |
| Pipline injection                        |
| Alternative backends                     |
| Optional package for generating program definitions from YAML files |
