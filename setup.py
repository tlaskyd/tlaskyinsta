import setuptools

with open('./README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='tlaskyinsta',
    version='1.0.0',
    author='David Tláskal',
    author_email='da.tlaskal@gmail.com',
    description='Python Instagram bot api.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/tlaskyd/tlaskyinsta',
    packages=['tlaskyinsta'],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.8',
)
