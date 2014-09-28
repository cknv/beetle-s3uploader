from setuptools import setup

setup(
    name='beetle_s3uploader',
    author='Esben Sonne',
    author_email='esbensonne+code@gmail.com',
    description='Beetle plugin to upload the site to S3',
    url='https://github.com/cknv/beetle-s3uploader',
    license='MIT',
    packages=[
        'beetle_s3uploader'
    ],
    install_requires=[
        'boto'
    ]
)
