from setuptools import setup, find_packages

setup(
    name='wva',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'requests',
        'beautifulsoup4',
        'paramiko',
        'colorama',
    ],
    entry_points={
        'console_scripts': [
            'WVA=wva.main:main',
        ],
    },
    author='Your Name',
    author_email='your.email@example.com',
    description='A web vulnerability analyzer tool',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/yourusername/wva',  # Replace with your actual GitHub URL
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
