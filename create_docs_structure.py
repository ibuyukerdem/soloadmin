import os
import importlib.util

SEPARATOR = "\n\n---\n\n"  # Yeni eklenen veriler için ayraç


def read_file_content(file_path):
    """Bir dosyanın içeriğini UTF-8 formatında döndürür, yoksa boş string döner."""
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as file:
            return file.read()
    return ""


def append_to_file(file_path, content):
    """
    Mevcut bir dosyanın sonuna yeni içerik ekler.
    """
    existing_content = read_file_content(file_path)
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(existing_content + SEPARATOR + content)


def write_file(file_path, content):
    """
    Yeni bir dosya oluşturur veya mevcutsa yeni verileri sonuna ekler.
    """
    if os.path.exists(file_path):
        append_to_file(file_path, content)
    else:
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(content)


def get_app_metadata(app_path):
    """
    apps.py dosyasındaki AppConfig sınıfından verbose_name ve description bilgilerini çeker.
    Eğer herhangi bir veri bulunamazsa, boş değer döner.
    """
    apps_file = os.path.join(app_path, "apps.py")
    if not os.path.exists(apps_file):
        print(f"{apps_file} bulunamadı.")
        return {"verbose_name": "", "description": ""}

    try:
        # apps.py dosyasını yükle
        spec = importlib.util.spec_from_file_location("apps", apps_file)
        apps_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(apps_module)

        # AppConfig sınıfını bul
        for attr_name in dir(apps_module):
            attr = getattr(apps_module, attr_name)
            if isinstance(attr, type) and issubclass(attr, apps_module.AppConfig) and attr != apps_module.AppConfig:
                app_config = attr()
                verbose_name = getattr(app_config, "verbose_name", None)
                description = getattr(app_config, "description", None)

                return {
                    "verbose_name": verbose_name or "",
                    "description": description or ""
                }

        print(f"AppConfig sınıfı {apps_file} içinde bulunamadı.")
    except Exception as e:
        print(f"Metadata alınırken hata oluştu: {e}")

    return {"verbose_name": "", "description": ""}


def generate_app_structure(root_path):
    """
    Proje kök dizinindeki tüm app'lerin ve sub-app'lerin dizin yapısını çıkarır.
    """
    structure = []
    for app_name in os.listdir(root_path):
        app_path = os.path.join(root_path, app_name)
        if os.path.isdir(app_path) and not app_name.startswith("."):
            sub_apps = [
                name for name in os.listdir(app_path)
                if os.path.isdir(os.path.join(app_path, name)) and name != "docs"
            ]
            structure.append({"app": app_name, "sub_apps": sub_apps})
    return structure


def create_docs_structure(root_path, app_name=None, sub_apps=None):
    """
    Proje dokümantasyonu ve app/sub-app dokümantasyon yapısını oluşturur ve içerik ekler.

    Args:
        root_path (str): Proje kök dizini.
        app_name (str): Ana app adı (varsayılan: None).
        sub_apps (list): Sub-app isimlerini içeren liste (varsayılan: None).
    """
    # 1. Root-level docs dizinini oluştur
    docs_path = os.path.join(root_path, "docs")
    os.makedirs(docs_path, exist_ok=True)

    # Root-level dosyaları oluştur
    structure = generate_app_structure(root_path)
    root_doc_files = {
        "README.md": "# Proje Dokümantasyonu\n\nBu proje Django tabanlı bir uygulamadır.",
        "DEVELOPERS_GUIDE.md": "# Geliştirici Rehberi\n\nKod yapısı ve test süreçleri burada açıklanır.",
        "API_REFERENCE.md": "# API Referansı\n\nTüm API endpoint'leri ve açıklamaları burada yer alır.",
        "APPS_OVERVIEW.md": (
                "# App ve Sub-App Açıklamaları\n\n"
                + "\n".join(
            f"- {app['app']}: {', '.join(app['sub_apps']) or 'Sub-app bulunmuyor'}"
            for app in structure
        )
        ),
        "FRONTEND_GUIDE.md": "# Frontend Rehberi\n\nAPI'nin frontend ile nasıl kullanılacağı hakkında bilgi içerir."
    }
    for file_name, content in root_doc_files.items():
        file_path = os.path.join(docs_path, file_name)
        write_file(file_path, content)

    # Ana app için docs oluştur
    if app_name:
        app_docs_path = os.path.join(root_path, app_name, "docs")
        os.makedirs(app_docs_path, exist_ok=True)

        # App metadata bilgilerini çek
        app_metadata = get_app_metadata(os.path.join(root_path, app_name))

        # Ana app dokümantasyon dosyalarını oluştur
        app_doc_files = {
            "README.md": f"# {app_metadata.get('verbose_name', app_name.capitalize())}\n\n{app_metadata.get('description', '')}",
            "API_REFERENCE.md": f"# {app_metadata.get('verbose_name', app_name.capitalize())} API Referansı\n\n{app_metadata.get('description', '')}",
        }
        for file_name, content in app_doc_files.items():
            file_path = os.path.join(app_docs_path, file_name)
            write_file(file_path, content)

        # Sub-app'ler varsa onların dokümantasyonlarını oluştur
        if sub_apps:
            for sub_app in sub_apps:
                sub_app_docs_path = os.path.join(root_path, app_name, sub_app, "docs")
                os.makedirs(sub_app_docs_path, exist_ok=True)

                sub_app_doc_files = {
                    "README.md": f"# {sub_app.capitalize()} Sub-App\n\nBu sub-app {sub_app} ile ilgili detayları içerir.",
                    "API_REFERENCE.md": f"# {sub_app.capitalize()} API Referansı\n\n{sub_app} ile ilgili API endpoint'leri burada açıklanır.",
                }
                for file_name, content in sub_app_doc_files.items():
                    file_path = os.path.join(sub_app_docs_path, file_name)
                    write_file(file_path, content)

    print("Dokümantasyon yapısı başarıyla oluşturuldu.")


def interactive_docs_setup():
    """
    Kullanıcı dostu ve etkileşimli bir dokümantasyon yapılandırma aracı.
    """
    print("Django Dokümantasyon Yapılandırıcısı")
    print("0: Root-Level (Ana Dizin)")
    print("1: App için dokümantasyon oluştur")
    print("2: Sub-App için dokümantasyon oluştur")

    choice = input("Seçiminizi yapın (0/1/2): ").strip()

    if choice == "0":
        create_docs_structure(root_path=os.getcwd())
    elif choice == "1":
        app_name = input("App adını girin: ").strip()
        create_docs_structure(root_path=os.getcwd(), app_name=app_name)
    elif choice == "2":
        app_name = input("Ana app adını girin: ").strip()
        sub_apps = input("Sub-app adlarını virgülle ayırarak girin: ").strip().split(",")
        create_docs_structure(root_path=os.getcwd(), app_name=app_name, sub_apps=sub_apps)
    else:
        print("Geçersiz seçim. Tekrar deneyin.")


# Script çalıştırıldığında interaktif modda başlatılır
if __name__ == "__main__":
    interactive_docs_setup()
