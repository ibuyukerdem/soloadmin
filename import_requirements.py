import subprocess
import os

# Sanal ortamın doğru yolunu belirtin
venv_path = "/home/solofor/soloadmin/.venv"  # .venv'in bulunduğu doğru yol

# requirements.txt dosyasını kontrol edin
requirements_file = "/home/solofor/soloadmin/requirements.txt"  # requirements.txt'nin tam yolu

if not os.path.exists(requirements_file):
    print(f"{requirements_file} bulunamadı. Lütfen dosyayı kontrol edin.")
else:
    # Virtual environment pip path
    pip_path = os.path.join(venv_path, "bin", "pip")  # Linux ve macOS için
    if os.name == "nt":  # Windows
        pip_path = os.path.join(venv_path, "Scripts", "pip.exe")

    # Pip komutunu çalıştır
    try:
        subprocess.run([pip_path, "install", "-r", requirements_file], check=True)
        print(f"{requirements_file} dosyasındaki kütüphaneler yüklendi.")
    except Exception as e:
        print(f"Hata oluştu: {e}")
