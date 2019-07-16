# What's new
## v0.0.2

From version v0.0.2 Flython code contains [formatted string literals](https://docs.python.org/3.6/reference/lexical_analysis.html#f-strings),
**therefore minimum required python version is 3.6.**

# Getting started

Use scripts from the `examples` directory to begin. Each example
script can be executed from shell or within an interactive session.

For interactive session mode type

$ from flython import api

then prepare the simulation instance using

$ instance = api.load('path/to/model.py')
$ simdata = instance.run()

