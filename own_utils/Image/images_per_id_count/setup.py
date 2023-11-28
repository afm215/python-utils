from setuptools import setup
from Cython.Build import cythonize

setup(
    ext_modules=cythonize(
        ['nb_imgs_per_id_count.pyx'],  # Python code file with primes() function
        annotate=False),                 # enables generation of the html annotation file
)