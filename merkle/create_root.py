import os
import json
import re
import sys
import subprocess
import io

# Đảm bảo in ra UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
EMPLOYEE_FOLDER = os.path.join(CURRENT_DIR, "../employees")
ROOTS_FOLDER = os.path.join(CURRENT_DIR, "../roots")
REQUIRED_DEPTH = 3
TOTAL_LEAVES = 2 ** REQUIRED_DEPTH

def str_to_bigint(s):
    return int.from_bytes(s.encode(), 'big')

def poseidon_hash(inputs):
    if len(inputs) != 2:
        raise ValueError("Poseidon hash requires exactly 2 inputs.")
    js_path = os.path.join(CURRENT_DIR, "poseidon_hash.js")
    result = subprocess.run(
        ["node", js_path, str(inputs[0]), str(inputs[1])],
        capture_output=True,
        text=True,
        check=True
    )
    return int(result.stdout.strip())

def poseidon_hash_leaf(email, secret):
    return poseidon_hash([str_to_bigint(email), str_to_bigint(secret)])

def poseidon_hash_node(left, right):
    return poseidon_hash([left, right])

def build_merkle_tree(hashed_leaves):
    current_level = hashed_leaves
    tree = [current_level]
    while len(current_level) > 1:
        next_level = []
        for i in range(0, len(current_level), 2):
            left = current_level[i]
            right = current_level[i + 1] if i + 1 < len(current_level) else left
            next_level.append(poseidon_hash_node(left, right))
        tree.append(next_level)
        current_level = next_level
    return tree, tree[-1][0]

def main():
    os.makedirs(ROOTS_FOLDER, exist_ok=True)
    for filename in os.listdir(EMPLOYEE_FOLDER):
        if filename.startswith("employees_") and filename.endswith(".json"):
            role = re.sub(r'^employees_|\.json$', '', filename)
            employee_file = os.path.join(EMPLOYEE_FOLDER, filename)
            with open(employee_file, "r", encoding="utf-8") as f:
                employees = json.load(f)
            # Hash all leaves
            hashed_leaves = [poseidon_hash_leaf(emp["email"], emp["secret"]) for emp in employees]
            while len(hashed_leaves) < TOTAL_LEAVES:
                hashed_leaves.append(0)
            # Build Merkle Tree
            tree, root = build_merkle_tree(hashed_leaves)
            # Export root and leaves
            root_file = os.path.join(ROOTS_FOLDER, f"{role}.json")
            with open(root_file, "w", encoding="utf-8") as f:
                json.dump({
                    "root": str(root),
                    "leaves": [str(leaf) for leaf in hashed_leaves]
                }, f, indent=2)
            print(f"✅ Exported root and leaves for role '{role}' to {root_file}")

if __name__ == "__main__":
    main()