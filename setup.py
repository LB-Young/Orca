from setuptools import setup, find_packages

install_requires = [
'smtplib',
'serpapi',
'pydantic',
'openai',
'together',
'groq',
'dotenv'
]

setup(
    name='Orca',
    version='0.0.1',
    description='Alanguage for Agent tasks',
    package_dir={'': 'src'},
    packages=find_packages('src'),
    author='YoungL',
    license='can not used for business without pay',
    install_requires=install_requires,
    python_requires='>=3.10',
)