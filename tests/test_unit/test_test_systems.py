

from openmm_systems.test_systems import (
    LennardJonesPair,
    LysozymeImplicit,
)

def test_LennardJonesPair():

    # just touch a bunch of stuff to make sure the work

    testsys = LennardJonesPair()
    assert hasattr(testsys, 'mdtraj_topology')
    assert hasattr(testsys, 'topology')
    assert hasattr(testsys, 'system')
    assert hasattr(testsys, 'positions')
    assert hasattr(testsys, 'receptor_indices')
    assert hasattr(testsys, 'ligand_indices')

def test_Lysozyme():

    testsys = LysozymeImplicit()

    assert hasattr(testsys, 'mdtraj_topology')
    assert hasattr(testsys, 'topology')
    assert hasattr(testsys, 'system')
    assert hasattr(testsys, 'positions')

    # TODO: these really should be here.. but they aren't
    # assert hasattr(testsys, 'receptor_indices')
    # assert hasattr(testsys, 'ligand_indices')
