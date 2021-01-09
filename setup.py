import setuptools

with open('./README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='tlasky_insta',
    version='1.0.0',
    author='David Tláskal',
    author_email='da.tlaskal@gmail.com',
    description='Python Instagram bot api.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/tlaskyd/tlaskyinsta',
    packages=['tlasky_insta'],
    classifiers=['MIT License'],
    python_requires='>=3.7.3',
)
