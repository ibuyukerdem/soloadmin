import subprocess

# Pip freeze çıktısını al ve requirements.txt'ye yaz
with open("requirements.txt", "w") as f:
    subprocess.run(["pip", "freeze"], stdout=f)