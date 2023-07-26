# Utils Package

## Installation
Clone this repo and run 

```
pip install -e ./
```

## Important notice:
This package uses several dependencies. (for instance the module ML.torch will depend in the torch module). Be aware that these dependecies are not explicitely required within setup.py, and thus some functions can crash on runtime if the associated dependencies are not installed. This package is an utility package and thus should not pollute your environment. It has been chosen to give to the user the choice to install what he truly needs.  