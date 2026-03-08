
from setuptools import setup, find_packages
import os # Added import os

setup(
    name='pycugrep',
    version='0.1.1',
    packages=['pycugrep'],
    package_dir={'pycugrep': 'pycugrep'},
    entry_points={
        'console_scripts': [
            'cugrep = pycugrep.cli:main',
        ],
    },
    package_data={
        'pycugrep': ['bin/cugrep'],
    },
    include_package_data=True,
    zip_safe=False, # Required for packages with binary data
    python_requires='>=3.8',
    install_requires=[
        'importlib_resources; python_version<"3.9"',
        'rapids-logger'
    ],
    description='A GPU-accelerated grep tool built with cuDF.',
    long_description=open('README.md').read() if os.path.exists('README.md') else '',
    long_description_content_type='text/markdown',
    url='https://github.com/your-repo/pycugrep', # Replace with your project URL
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: POSIX :: Linux',
        'Topic :: Utilities',
    ],
)
