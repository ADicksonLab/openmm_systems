

from scipy.integrate import quadrature

class LennardJonesPair(TestSystem):

    """Create a pair of Lennard-Jones particles.

    Parameters
    ----------
    mass : simtk.unit.Quantity with units compatible with amu, optional, default=39.9*amu
       The mass of each particle.
    epsilon : simtk.unit.Quantity with units compatible with kilojoules_per_mole, optional, default=1.0*kilocalories_per_mole
       The effective Lennard-Jones sigma parameter.
    sigma : simtk.unit.Quantity with units compatible with nanometers, optional, default=3.350*angstroms
       The effective Lennard-Jones sigma parameter.

    Examples
    --------

    Create Lennard-Jones pair.

    >>> test = LennardJonesPair()
    >>> system, positions = test.system, test.positions
    >>> thermodynamic_state = ThermodynamicState(temperature=300.0*unit.kelvin)
    >>> binding_free_energy = test.get_binding_free_energy(thermodynamic_state)

    Create Lennard-Jones pair with different well depth.

    >>> test = LennardJonesPair(epsilon=11.0*unit.kilocalories_per_mole)
    >>> system, positions = test.system, test.positions
    >>> thermodynamic_state = ThermodynamicState(temperature=300.0*unit.kelvin)
    >>> binding_free_energy = test.get_binding_free_energy(thermodynamic_state)

    Create Lennard-Jones pair with different well depth and sigma.

    >>> test = LennardJonesPair(epsilon=7.0*unit.kilocalories_per_mole, sigma=4.5*unit.angstroms)
    >>> system, positions = test.system, test.positions
    >>> thermodynamic_state = ThermodynamicState(temperature=300.0*unit.kelvin)
    >>> binding_free_energy = test.get_binding_free_energy(thermodynamic_state)

    """

    def __init__(self, mass=39.9 * unit.amu, sigma=3.350 * unit.angstrom, epsilon=10.0 * unit.kilocalories_per_mole, **kwargs):

        TestSystem.__init__(self, **kwargs)

        # Store parameters
        self.mass = mass
        self.sigma = sigma
        self.epsilon = epsilon

        # Charge must be zero.
        charge = 0.0 * unit.elementary_charge

        # Create an empty system object.
        system = openmm.System()

        # Create a NonbondedForce object with no cutoff.
        force = openmm.NonbondedForce()
        force.setNonbondedMethod(openmm.NonbondedForce.NoCutoff)

        # Create positions.
        positions = unit.Quantity(np.zeros([2, 3], np.float32), unit.angstrom)
        # Move the second particle along the x axis to be at the potential minimum.
        positions[1, 0] = 2.0**(1.0 / 6.0) * sigma

        # Create first particle.
        system.addParticle(mass)
        force.addParticle(charge, sigma, epsilon)

        # Create second particle.
        system.addParticle(mass)
        force.addParticle(charge, sigma, epsilon)

        # Add the nonbonded force.
        system.addForce(force)

        # Store system and positions.
        self.system, self.positions = system, positions

        # Store ligand and receptor particle indices.
        self.ligand_indices = [0]
        self.receptor_indices = [1]

        # Create topology.
        topology = app.Topology()
        element = app.Element.getBySymbol('Ar')
        chain = topology.addChain()
        residue = topology.addResidue('Ar', chain)
        topology.addAtom('Ar', element, residue)
        residue = topology.addResidue('Ar', chain)
        topology.addAtom('Ar', element, residue)
        self.topology = topology

    def get_binding_free_energy(self, thermodynamic_state):
        """
        Compute the binding free energy of the two particles at the given thermodynamic state.

        Parameters
        ----------
        thermodynamic_state : ThermodynamicState
           The thermodynamic state specifying the temperature for which the binding free energy is to be computed.

        This is currently computed by numerical integration.

        """

        # Compute thermal energy.
        kT = kB * thermodynamic_state.temperature

        # Form the integrand function for integration in reduced units (r/sigma).
        platform = openmm.Platform.getPlatformByName('Reference')
        integrator = openmm.VerletIntegrator(1.0 * unit.femtoseconds)
        context = openmm.Context(self.system, integrator, platform)
        context.setPositions(self.positions)

        def integrand_openmm(xvec, args):
            """OpenMM implementation of integrand (for sanity checks)."""
            [context] = args
            positions = unit.Quantity(np.zeros([2, 3], np.float32), unit.angstrom)
            integrands = 0.0 * xvec
            for (i, x) in enumerate(xvec):
                positions[1, 0] = x * self.sigma
                context.setPositions(positions)
                state = context.getState(getEnergy=True)
                u = state.getPotentialEnergy() / kT  # effective energy
                integrand = 4.0 * pi * (x**2) * np.exp(-u)
                integrands[i] = integrand

            return integrands

        def integrand_numpy(x, args):
            """NumPy implementation of integrand (for speed)."""
            u = 4.0 * (self.epsilon) * (x**(-12) - x**(-6)) / kT
            integrand = 4.0 * pi * (x**2) * np.exp(-u)
            return integrand

        # Compute standard state volume
        V0 = (unit.liter / (unit.AVOGADRO_CONSTANT_NA * unit.mole)).in_units_of(unit.angstrom**3)

        # Integrate the free energy of binding in unitless coordinate system.
        xmin = 0.15  # in units of sigma
        xmax = 6.0  # in units of sigma

        [integral, abserr] = quadrature(integrand_numpy, xmin, xmax, args=[context], maxiter=500)
        # correct for performing unitless integration
        integral = integral * (self.sigma ** 3)

        # Correct for actual integration volume (which exceeds standard state volume).
        rmax = xmax * self.sigma
        Vint = (4.0 / 3.0) * pi * (rmax**3)
        integral = integral * (V0 / Vint)

        # Clean up.
        del context, integrator

        # Compute standard state binding free energy.
        binding_free_energy = -kT * np.log(integral / V0)

        return binding_free_energy
