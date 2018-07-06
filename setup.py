import setuptools

requires = ["terminaltables >= 3.1.0"]

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="hpc_acm_cli",
    version="1.0.0",
    author="Robert Zhang",
    description="HPC ACM client",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
    entry_points = {
        'console_scripts': [
            'hpc-node=hpc_acm_cli.node:main',
            'hpc-clus=hpc_acm_cli.clus:main',
            'hpc-diag=hpc_acm_cli.diag:main',
        ],
    },
    install_requires=requires
)
