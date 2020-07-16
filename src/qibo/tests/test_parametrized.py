import numpy as np
import pytest
import qibo
from qibo.models import Circuit
from qibo import gates

_BACKENDS = ["custom", "defaulteinsum", "matmuleinsum"]


@pytest.mark.parametrize("backend", _BACKENDS)
def test_rx_parameter_setter(backend):
    """Check that the parameter setter of RX gate is working properly."""
    def exact_state(theta):
        phase = np.exp(1j * theta / 2.0)
        gate = np.array([[phase.real, -1j * phase.imag],
                        [-1j * phase.imag, phase.real]])
        return gate.dot(np.ones(2)) / np.sqrt(2)

    original_backend = qibo.get_backend()
    qibo.set_backend(backend)
    theta = 0.1234
    c = Circuit(1)
    c.add(gates.H(0))
    c.add(gates.RX(0, theta=theta))
    final_state = c().numpy()
    target_state = exact_state(theta)
    np.testing.assert_allclose(final_state, target_state)

    theta = 0.4321
    c.queue[-1].parameter = theta
    final_state = c().numpy()
    target_state = exact_state(theta)
    np.testing.assert_allclose(final_state, target_state)
    qibo.set_backend(original_backend)


@pytest.mark.parametrize("backend", _BACKENDS)
def test_circuit_update_parameters_with_list(backend):
    """Check updating parameters of circuit with list."""
    original_backend = qibo.get_backend()
    qibo.set_backend(backend)
    def create_circuit(params):
        c = Circuit(3)
        c.add(gates.RX(0, theta=params[0]))
        c.add(gates.RY(1, theta=params[1]))
        c.add(gates.CZ(1, 2))
        c.add(gates.fSim(0, 2, theta=params[2][0], phi=params[2][1]))
        c.add(gates.H(2))
        return c

    params0 = [0.123, 0.456, (0.789, 0.321)]
    params1 = [0.987, 0.654, (0.321, 0.123)]
    c = create_circuit(params0)
    target_c = create_circuit(params1)
    c.update_parameters(params1)

    np.testing.assert_allclose(c(), target_c())


@pytest.mark.parametrize("backend", _BACKENDS)
def test_circuit_update_parameters_with_dictionary(backend):
    """Check updating parameters of circuit with list."""
    original_backend = qibo.get_backend()
    qibo.set_backend(backend)
    def create_circuit(params):
        c = Circuit(3)
        c.add(gates.X(0))
        c.add(gates.X(2))
        c.add(gates.ZPow(0, theta=params[0]))
        c.add(gates.RZ(1, theta=params[1]))
        c.add(gates.CZ(1, 2))
        c.add(gates.CZPow(0, 2, theta=params[2]))
        c.add(gates.H(2))
        c.add(gates.Unitary(params[3], 1))
        return c

    params0 = [0.123, 0.456, 0.789, np.random.random((2, 2))]
    params1 = [0.987, 0.654, 0.321, np.random.random((2, 2))]
    c = create_circuit(params0)
    target_c = create_circuit(params1)
    param_dict = {c.queue[i]: p for i, p in zip([2, 3, 5, 7], params1)}
    print(c.parametrized_gates)
    print(param_dict)
    c.update_parameters(param_dict)

    np.testing.assert_allclose(c(), target_c())
