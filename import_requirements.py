import subprocess
import os

# Virtual environment path'i belirleyin (örneğin: './venv')
venv_path = "./venv"

# requirements.txt dosyasını kontrol edin
requirements_file = "requirements.txt"

if not os.path.exists(requirements_file):
    print(f"{requirements_file} bulunamadı. Lütfen dosyayı kontrol edin.")
else:
    # Pip'i requirements.txt ile çalıştırın
    try:
        # Virtual environment pip path
        pip_path = os.path.join(venv_path, "bin", "pip")  # Unix tabanlı sistemler için
        if os.name == "nt":  # Windows
            pip_path = os.path.join(venv_path, "Scripts", "pip.exe")

        # Pip komutunu çalıştır
        subprocess.run([pip_path, "install", "-r", requirements_file], check=True)
        print(f"{requirements_file} dosyasındaki kütüphaneler yüklendi.")
    except Exception as e:
        print(f"Hata oluştu: {e}")
