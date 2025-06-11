from distutils.core import setup

setup(
    name='mkdocs_exam',
    version='0.0.41',
    packages=['mkdocs_exam',],
    package_data={'mkdocs_exam': ['css/*', 'js/*']},
    include_package_data=True,
    license='Apache License 2.0',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/kjanat/mkdocs-exam',
    description='A mkdocs plugin to create an exam in your markdown document.',
    author='Sebastian Jörz',
    author_email='sjoerz@skyface.de',
    install_requires=[
        "mkdocs",
    ],
    entry_points={
        'mkdocs.plugins': [
            'mkdocs-exam = mkdocs_exam.plugin:MkDocsExamPlugin',
        ]
    }
)
