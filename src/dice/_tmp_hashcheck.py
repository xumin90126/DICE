import hashlib
import os

BASE = os.path.dirname(os.path.abspath(__file__))

targets = [
    "registry.py",
    "bootstrap.py",
    os.path.join("runtime", "composition", "shadow", "capability_runtime", "capability_loader.py"),
]

def md5(path):
    p = os.path.join(BASE, path)
    if not os.path.exists(p):
        return "MISSING"
    with open(p, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()

for t in targets:
    print(f"{t}  {md5(t)}")

# Layer 1-8 aggregate hash (files under runtime/ excluding composition/shadow)
print("\n=== runtime/ top-level dirs ===")
runtime = os.path.join(BASE, "runtime")
print(sorted(os.listdir(runtime)))
