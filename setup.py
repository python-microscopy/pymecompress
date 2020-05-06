#!/usr/bin/python

##################
# setup.py
#
# Copyright David Baddeley, 2009-2020
# d.baddeley@auckland.ac.nz
#
#
##################

def configuration(parent_package='', top_path=None):
    if os.path.exists('MANIFEST'):
        os.remove('MANIFEST')
    
    from numpy.distutils.misc_util import Configuration
    config = Configuration(None, parent_package, top_path)
    
    config.set_options(
        ignore_setup_xxx_py=True,
        assume_default_configuration=True,
        delegate_options_to_subpackages=True,
        #quiet=True,
    )
    
    config.add_subpackage('pymecompress')
    config.get_version('pymecompress/version.py')
    return config


if __name__ == '__main__':
    import setuptools
    import os
    from distutils.command.sdist import sdist
    from numpy.distutils.core import setup


    with open('README.md', 'r') as f:
        long_description = f.read()

    setup(name='pymecompress',
        description='Compression for photon-noise limited images which keeps losses within the Poisson noise envelope',
        author='David Baddeley',
        author_email='david.baddeley@yale.edu',
        url='https://github.com/python-microscopy/pymecompress',
        long_description=long_description,
        long_description_content_type="text/markdown",
        license="BSD",
        install_requires=['numpy'],
        classifiers=[
            'Development Status :: 3 - Alpha',
            # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
            'License :: OSI Approved :: BSD License', # Again, pick a license
            'Programming Language :: Python :: 2.7', #Specify which python versions that you want to support
            'Programming Language :: Python :: 3.6',
            'Programming Language :: Python :: 3.7',
        ],
        cmdclass={'sdist': sdist},
        configuration=configuration)
    
    
