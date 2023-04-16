from setuptools import setup


setup(
    name="gdot",
    setup_requires="setupmeta",
    versioning="branch(main):dev",
    author="Zoran Simic zoran@simicweb.com",
    python_requires='>=3.6',
    url="https://github.com/zsimic/gdot",
    entry_points={
       "console_scripts": [
           "gdot = gdot.commands:main",
        ],
    },
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        # "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "Operating System :: MacOS",
        "Operating System :: POSIX",
        "Operating System :: POSIX :: Linux",
        "Operating System :: Unix",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: Implementation :: CPython",
        "Topic :: Software Development :: Libraries",
        "Topic :: System :: Installation/Setup",
        "Topic :: Utilities",
    ],
    project_urls={
        "Documentation": "https://github.com/codrsquad/gdot/wiki",
        "Release notes": "https://github.com/codrsquad/gdot/wiki/Release-notes",
        "Source": "https://github.com/codrsquad/gdot",
    },
)
