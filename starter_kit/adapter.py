#!/usr/bin/env python3
"""LoomQ submission adapter contract v1.0.

This file intentionally contains no scoring implementation. Teams may implement
the functions directly or delegate to another language/runtime with subprocess.
"""

from typing import Any, Dict, List, Tuple

import os
import tempfile

from datetime import datetime, timezone

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

            if line.strip().startswith("cx "):
                line = line.replace("cx", "cnot")

            if line.strip().startswith("measure") and "->" in line:
                parts = line.strip().rstrip(";").split(" -> ")
                line = f"{parts[1]} = {parts[0]};"

            if line.strip().startswith("ccx "):
                line = line.replace("ccx ", "ccnot ")

            if line.strip().startswith("cu1("):
                angle = line.split("(")[1].split(")")[0]
                qubits = line.split(")")[1].strip().rstrip(";")
                qa = qubits.split(",")[0].strip()
                qb = qubits.split(",")[1].strip()

                new_lines.append(f"rz({angle}/2) {qa};")
                new_lines.append(f"cnot {qa}, {qb};")
                new_lines.append(f"rz(-{angle}/2) {qb};")
                new_lines.append(f"cnot {qa}, {qb};")
                new_lines.append(f"rz({angle}/2) {qb};")
                continue

            if line.strip().startswith("sdg "):
                qubit = line.strip().replace("sdg ", "").rstrip(";")
                line = f"rz(-pi/2) {qubit};"

            if line.strip().startswith("s "):
                qubit = line.strip().replace("s ", "").rstrip(";")
                line = f"rz(pi/2) {qubit};"

            if line.strip().startswith("tdg "):
                qubit = line.strip().replace("tdg ", "").rstrip(";")
                line = f"rz(-pi/4) {qubit};"

            if line.strip().startswith("t "):
                qubit = line.strip().replace("t ", "").rstrip(";")
                line = f"rz(pi/4) {qubit};"

            new_lines.append(line)

        result = "\n".join(new_lines)
        return result

    elif target == "spinq":
        new_lines = []
        lines = qasm_str.split("\n")

        for line in lines:
            if line.strip().startswith("cu1("):
                angle = line.split("(")[1].split(")")[0]
                qubits = line.split(")")[1].strip().rstrip(";")
                qa = qubits.split(",")[0].strip()
                qb = qubits.split(",")[1].strip()
                
                new_lines.append(f"u1({angle}/2) {qa};")
                new_lines.append(f"cx {qa}, {qb};")
                new_lines.append(f"u1(-{angle}/2) {qb};")
                new_lines.append(f"cx {qa}, {qb};")
                new_lines.append(f"u1({angle}/2) {qb};")
                continue
            
            new_lines.append(line)
    
        results = "\n".join(new_lines)
        return results

    elif target == "originq":
        new_lines = []
        lines = qasm_str.split("\n")
        for line in lines:
            line = line.replace(";", "")

            if line.strip().startswith("OPENQASM"):
                continue

            if line.strip().startswith("include"):
                continue

            if "qreg" in line:
                parts = line.split("[")
                number = parts[1].split("]")
                line = f"QINIT {number[0]}"

            if "creg" in line:
                parts = line.split("[")
                number = parts[1].split("]")
                line = f"CREG {number[0]}"

            if line.strip().startswith("h "):
                line = line.replace("h ", "H ")

            if line.strip().startswith("cx "):
                line = line.replace("cx ", "CNOT ")

            if line.strip().startswith("measure "):
                line = line.replace("measure ", "MEASURE ")
                line = line.replace(" -> ", ",")

            if line.strip().startswith("x "):
                line = line.replace("x ", "X ")

            if line.strip().startswith("swap "):
                line = line.replace("swap ", "SWAP ")

            if line.strip().startswith("sdg "):
                line = line.replace("sdg ", "SDAG ")

            if line.strip().startswith("s "):
                line = line.replace("s ", "S ")

            if line.strip().startswith("tdg "):
                line = line.replace("tdg ", "TDAG ")

            if line.strip().startswith("t "):
                line = line.replace("t ", "T ")

            if line.strip().startswith("ccx "):
                line = line.replace("ccx ", "TOFFOLI ")

            if "rz(" in line:
                line = line.replace("rz(", "RZ(")

            if "ry(" in line:
                line = line.replace("ry(", "RY(")

            if "cu1(" in line:
                line = line.replace("cu1(", "CU1(")

            new_lines.append(line)

        result = "\n".join(new_lines)   
        return result
        

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
        "counts": dict(counts),
        "bit_order": "little",
        "timestamp": datetime.now(timezone.utc).isoformat()
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
            "counts": dict(counts),
            "bit_order": "little",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

    elif target == "originq":
        import pyqpanda as pq

        machine = pq.CPUQVM()
        machine.init_qvm()

        try:
            # 兼容不同版本 pyqpanda 接口
            if hasattr(pq, 'convert_qasm_string_to_qprog'):
                prog, qreg, creg = pq.convert_qasm_string_to_qprog(qasm_str, machine)
            else:
                prog = pq.convert_qasm_to_qprog(qasm_str, machine)
                # 如果接口只返回 prog，需要从机器获取比特列表
                qreg = machine.get_allocate_qubits()
                creg = machine.get_allocate_cbits()
        except Exception as e:
            raise RuntimeError(f"QASM 转译失败，请检查语法兼容性: {e}")

        # 3. 运行线路
        # 使用 run_with_configuration 进行多次测量采样 (shots)
        result = machine.run_with_configuration(prog, creg, shots)
        
        # 4. 统计结果
        # pyqpanda 返回的 counts 是以十进制或二进制字符串作为 key
        # 我们确保将其标准化为二进制 key，如 "00", "11"
        raw_counts = result
        formatted_counts = {}
        
        # 获取比特总数，以便将十进制格式化为对应长度的二进制串
        num_bits = len(creg)
        for key, val in raw_counts.items():
            trimmed = key[-num_bits:]  
            reversed_key = trimmed[::-1]
            formatted_counts[reversed_key] = val

    # 5. 释放量子虚拟机器资源
    machine.finalize()

    return {
        "backend": "originq_cpu_simulator",
        "job_id": "originq-sim-job-local",
        "shots": shots,
        "counts": formatted_counts,
        "bit_order": "little",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


def agent_chat(prompt: str) -> str:
    """Optional L2 entry point using the documented LOOMQ_LLM_* environment."""
    raise NotImplementedError("L2 is optional; implement agent_chat(prompt) to enter")


def compile_hybrid(hybrid_qasm_str: str) -> Tuple[List[str], str]:
    """Optional L3 entry point. Return quantum operations and RISC-V assembly."""
    raise NotImplementedError(
        "L3 is optional; implement compile_hybrid(hybrid_qasm_str) to enter"
    )
