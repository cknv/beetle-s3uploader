from setuptools import setup

setup(
    name='beetle_s3upload',
    author='Esben Sonne',
    author_email='esbensonne@gmail.com',
    packages=[
        'beetle_s3upload'
    ],
    install_requires=[
        'boto==2.32.1'
    ]
)
