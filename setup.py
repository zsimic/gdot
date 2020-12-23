from setuptools import setup


if __name__ == "__main__":
    setup(
        name="gdot",
        setup_requires="setupmeta",
        versioning="dev",
        author="Zoran Simic zoran@simicweb.com",
        url="https://github.com/zsimic/",
        entry_points={
           "console_scripts": [
               "gdot = gdot.commands:main",
            ],
        },
        classifiers=[
            "Development Status :: 5 - Production/Stable",
            "Environment :: Console",
            "Intended Audience :: Developers",
            "Intended Audience :: End Users/Desktop",
            "Operating System :: MacOS",
            "Operating System :: POSIX",
            "Operating System :: POSIX :: Linux",
            "Operating System :: Unix",
            "Programming Language :: Python",
            "Programming Language :: Python :: 2",
            "Programming Language :: Python :: 2.7",
            "Programming Language :: Python :: 3",
            "Programming Language :: Python :: 3.6",
            "Programming Language :: Python :: 3.7",
            "Programming Language :: Python :: 3.8",
            "Programming Language :: Python :: 3.9",
            "Programming Language :: Python :: 3.10",
            "Programming Language :: Python :: Implementation :: CPython",
            "Topic :: Software Development :: Libraries",
            "Topic :: System :: Installation/Setup",
            "Topic :: Utilities",
        ],
    )
