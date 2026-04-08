from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from qiskit import QuantumCircuit
from qiskit.quantum_info import SparsePauliOp, Statevector
from sklearn.linear_model import Ridge

from common.metrics import compute_metrics
from common.sequential_features import build_scaler_state, scaled_input_vector


@dataclass(frozen=True)
class QRCConfig:
    n_qubits: int = 14
    window: int = 7
    input_scale: float = 1.2
    ridge_alpha: float = 1e-1
    seed: int = 7


@dataclass(frozen=True)
class QRCResult:
    predictions: pd.Series
    metrics: dict[str, float]


class ReuploadingQuantumReservoir:
    def __init__(self, *, config: QRCConfig) -> None:
        self.config = config
        rng = np.random.default_rng(config.seed)
        self.rx_weights = rng.uniform(0.6, 1.4, size=(config.n_qubits, 4))
        self.ry_weights = rng.uniform(-1.2, 1.2, size=(config.n_qubits, 4))
        self.bias = rng.uniform(-0.4, 0.4, size=config.n_qubits)
        self.entangling_angles = rng.uniform(-0.8, 0.8, size=config.n_qubits)
        self.observables = self._build_observables(config.n_qubits)

    @staticmethod
    def _build_observables(n_qubits: int) -> list[SparsePauliOp]:
        observables: list[SparsePauliOp] = []
        for q in range(n_qubits):
            z_label = ["I"] * n_qubits
            z_label[n_qubits - 1 - q] = "Z"
            observables.append(SparsePauliOp.from_list([("".join(z_label), 1.0)]))

        for q in range(n_qubits):
            x_label = ["I"] * n_qubits
            x_label[n_qubits - 1 - q] = "X"
            observables.append(SparsePauliOp.from_list([("".join(x_label), 1.0)]))

        for q in range(n_qubits):
            zz_label = ["I"] * n_qubits
            zz_label[n_qubits - 1 - q] = "Z"
            zz_label[n_qubits - 1 - ((q + 1) % n_qubits)] = "Z"
            observables.append(SparsePauliOp.from_list([("".join(zz_label), 1.0)]))
        return observables

    def _step_circuit(self, input_vector: np.ndarray) -> QuantumCircuit:
        circuit = QuantumCircuit(self.config.n_qubits)
        for q in range(self.config.n_qubits):
            angle_x = self.config.input_scale * float(self.rx_weights[q] @ input_vector) + self.bias[q]
            angle_y = self.config.input_scale * float(self.ry_weights[q] @ input_vector)
            circuit.rx(angle_x, q)
            circuit.ry(angle_y, q)

        for q in range(self.config.n_qubits - 1):
            circuit.cz(q, q + 1)
            circuit.rz(self.entangling_angles[q], q + 1)
        circuit.cz(self.config.n_qubits - 1, 0)
        circuit.rz(self.entangling_angles[-1], 0)
        return circuit

    def features_from_window(self, window_vectors: list[np.ndarray]) -> np.ndarray:
        circuit = QuantumCircuit(self.config.n_qubits)
        for vector in window_vectors:
            circuit.compose(self._step_circuit(vector), inplace=True)
        state = Statevector.from_instruction(circuit)
        features = [float(np.real(state.expectation_value(obs))) for obs in self.observables]
        return np.asarray(features, dtype=float)


def _quantum_input_vector(prev_y: float, row: pd.Series, *, scaler) -> np.ndarray:
    base = scaled_input_vector(prev_y, row, scaler=scaler)
    return base[:4]


def _feature_vector(quantum_features: np.ndarray, last_input: np.ndarray) -> np.ndarray:
    return np.concatenate([[1.0], last_input, quantum_features])


def fit_qrc_readout(train: pd.DataFrame, *, config: QRCConfig) -> tuple[ReuploadingQuantumReservoir, Ridge, object]:
    scaler = build_scaler_state(train)
    reservoir = ReuploadingQuantumReservoir(config=config)
    input_history: list[np.ndarray] = []
    feature_rows: list[np.ndarray] = []
    targets: list[float] = []

    prev_y = float(train.iloc[0]["y"])
    for idx in range(1, len(train)):
        row = train.iloc[idx]
        input_vector = _quantum_input_vector(prev_y, row, scaler=scaler)
        input_history.append(input_vector)
        if len(input_history) >= config.window:
            window_vectors = input_history[-config.window :]
            quantum_features = reservoir.features_from_window(window_vectors)
            feature_rows.append(_feature_vector(quantum_features, input_vector))
            targets.append(float(row["y"]))
        prev_y = float(row["y"])

    readout = Ridge(alpha=config.ridge_alpha)
    readout.fit(np.vstack(feature_rows), np.asarray(targets))
    return reservoir, readout, scaler


def forecast_qrc(
    train: pd.DataFrame,
    test: pd.DataFrame,
    *,
    config: QRCConfig,
) -> pd.Series:
    reservoir, readout, scaler = fit_qrc_readout(train, config=config)

    input_history: list[np.ndarray] = []
    prev_y = float(train.iloc[0]["y"])
    for idx in range(1, len(train)):
        row = train.iloc[idx]
        input_history.append(_quantum_input_vector(prev_y, row, scaler=scaler))
        prev_y = float(row["y"])

    preds: list[float] = []
    prev_y = float(train.iloc[-1]["y"])
    for idx in range(len(test)):
        row = test.iloc[idx]
        input_vector = _quantum_input_vector(prev_y, row, scaler=scaler)
        input_history.append(input_vector)
        window_vectors = input_history[-config.window :]
        quantum_features = reservoir.features_from_window(window_vectors)
        pred = float(readout.predict(_feature_vector(quantum_features, input_vector)[None, :])[0])
        pred = max(pred, 0.0)
        preds.append(pred)
        prev_y = pred
    return pd.Series(preds, name="y_pred")


def run_qrc(
    train: pd.DataFrame,
    test: pd.DataFrame,
    *,
    config: QRCConfig | None = None,
) -> QRCResult:
    active_config = config or QRCConfig()
    predictions = forecast_qrc(train, test, config=active_config)
    metrics = compute_metrics(test["y"].to_numpy(), predictions.to_numpy())
    return QRCResult(predictions=predictions, metrics=metrics)
