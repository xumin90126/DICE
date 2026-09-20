import hashlib, pathlib  
  
root = pathlib.Path('dice/runtime')  
files = []  
for p in sorted(root.rglob('*.py')):  
    sp = str(p)  
    if '__pycache__' in sp: continue  
    if 'composition' in sp: continue  
    files.append(p)  
hashes = [hashlib.md5(p.read_bytes()).hexdigest() for p in files]  
agg = hashlib.md5(''.join(hashes).encode()).hexdigest()  
print('aggregate:', agg, 'files:', len(files))  
