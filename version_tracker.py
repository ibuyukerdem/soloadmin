# version_tracker.py
from soloservice import __version__ as soloservice_version, __changelog__ as soloservice_changelog
from solofinance import __version__ as solofinance_version, __changelog__ as solofinance_changelog
from soloaccounting import __version__ as soloaccounting_version, __changelog__ as soloaccounting_changelog
from soloecommerce import __version__ as soloecommerce_version, __changelog__ as soloecommerce_changelog
from soloweb import __version__ as soloweb_version, __changelog__ as soloweb_changelog
from solopayment import __version__ as solopayment_version, __changelog__ as solopayment_changelog
from soloblog import __version__ as soloblog_version, __changelog__ as soloblog_changelog
from soloadmin import __version__ as project_version, __changelog__ as project_changelog

VERSIONS = {
    "soloadmin (Ana Proje)": {
        "version": project_version,
        "changelog": project_changelog,
    },
    "soloservice": {
        "version": soloservice_version,
        "changelog": soloservice_changelog,
    },
    "solofinance": {
        "version": solofinance_version,
        "changelog": solofinance_changelog,
    },
    "soloaccounting": {
        "version": soloaccounting_version,
        "changelog": soloaccounting_changelog,
    },
    "soloecommerce": {
        "version": soloecommerce_version,
        "changelog": soloecommerce_changelog,
    },
    "soloweb": {
        "version": soloweb_version,
        "changelog": soloweb_changelog,
    },
    "solopayment": {
        "version": solopayment_version,
        "changelog": solopayment_changelog,
    },
    "soloblog": {
        "version": soloblog_version,
        "changelog": soloblog_changelog,
    },
}

def print_versions():
    print("App Versiyonları ve Değişiklik Geçmişi:")
    for app_name, details in VERSIONS.items():
        print(f"\n{app_name}")
        print(f"  Sürüm: {details['version']}")
        print("  Değişiklikler:")
        print(details["changelog"])
        print("-" * 30)

if __name__ == "__main__":
    print_versions()
