#!/usr/bin/env python3
"""LoomQ submission adapter contract v1.0.

This file intentionally contains no scoring implementation. Teams may implement
the functions directly or delegate to another language/runtime with subprocess.
"""

from typing import Any, Dict, List, Tuple

import os
import tempfile

SUPPORTED_TARGETS = ("spinq", "originq", "braket")


def transpile(qasm_str: str, target: str) -> str:
    """Translate OpenQASM 2.0 into the target backend's native representation."""

    if target == "braket":
        new_lines = []

        lines = qasm_str.split("\n")
        for line in lines:

            if line.strip().startswith("OPENQASM"):
                line = line.replace("2.0", "3.0")

            if line.strip().startswith("include"):
                continue

            if "qreg" in line:
                parts = line.split("[")
                number = parts[1].split("]")
                line = f"qubit[{number[0]}] q;"

            if "creg" in line:
                parts = line.split("[")
                number = parts[1].split("]")
                line = f"bit[{number[0]}] c;"

            if line.strip().startswith("cx"):
                line = line.replace("cx", "cnot")

            if "measure q -> c" in line:
                line = "c = measure q;"

            new_lines.append(line)

        result = "\n".join(new_lines)

        return result

    if target == "spinq":
            return qasm_str


def run(qasm_str: str, target: str, shots: int) -> Dict[str, Any]:
    """Execute a circuit and return the unified result schema from the rules."""

    qasm3 = transpile(qasm_str, target) # call transpile() to get QASM 3.0

    if target == "braket":
        from braket.devices import LocalSimulator
        from braket.ir.openqasm import Program

        device = LocalSimulator()
        program = Program(source=qasm3)
        task = device.run(program, shots=shots)

        result = task.result()

        counts = result.measurement_counts

        return {
        "backend": "braket_local_simulator",
        "job_id": result.task_metadata.id,
        "shots": shots,
        "counts": counts,
        "bit_order": "little",
        "timestamp": "2026-08-05T17:19Z"
        }

    elif target == "spinq":
        from spinqit import BasicSimulatorConfig, get_basic_simulator, get_compiler

        tmp = tempfile.NamedTemporaryFile(
                mode="w", suffix=".qasm", delete=False, encoding="utf-8"
            )
        try:
            tmp.write(qasm_str)
            tmp.close()
            compiler = get_compiler("qasm")
            ir = compiler.compile(tmp.name, 0)
        finally:
            os.unlink(tmp.name)

        engine = get_basic_simulator()
        config = BasicSimulatorConfig()
        config.configure_shots(shots)

        result = engine.execute(ir, config)

        counts = result.counts

        return {
            "backend": "spinq_basic_simulator",
            "job_id": "spinq-local",
            "shots": shots,
            "counts": counts,
            "bit_order": "little",
            "timestamp": "2026-08-06T06:51Z"
        }


def agent_chat(prompt: str) -> str:
    """Optional L2 entry point using the documented LOOMQ_LLM_* environment."""
    raise NotImplementedError("L2 is optional; implement agent_chat(prompt) to enter")


def compile_hybrid(hybrid_qasm_str: str) -> Tuple[List[str], str]:
    """Optional L3 entry point. Return quantum operations and RISC-V assembly."""
    raise NotImplementedError(
        "L3 is optional; implement compile_hybrid(hybrid_qasm_str) to enter"
    )
