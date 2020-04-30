import nox

@nox.session(
    python=['3.6', '3.7', '3.8'],
    venv_backend="conda",
)
@nox.parametrize("openmm", [
    '7.4.1',
    '7.3.1',
])
def test(session, openmm):
    """Test with conda as the installer."""

    # install the pip things first
    session.install("-r", ".jubeo/requirements.txt")
    session.install("-r", "envs/test/requirements.in")
    session.install("-r", "envs/test/self.requirements.txt")

    # install conda specific things here
    session.conda_install('-c', 'omnia',
                          f'openmm={openmm}')

    session.run("inv", "py.tests-all", "-t", f"test-user-conda_{session.python}")

@nox.session(
    python=['3.6', '3.7', '3.8', 'pypy3']
)
def test_docs(session):
    """Test using basic pip based installation."""

    session.install("-r", ".jubeo/requirements.txt")
    session.install("-r", "envs/test/requirements.in")
    session.install("-r", "envs/test/self.requirements.txt")

    # TODO replace with doit tasks to make things faster. this needs
    # to be done beforehand because the build env is particular, and
    # is different than the test env

    # session.run("inv", "docs.tangle")

    session.run("inv", "docs.test", "-t", f"test-docs_{session.python}")
