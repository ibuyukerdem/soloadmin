# soloadmin/admin.py

from django.contrib import admin
from django.urls import path
from django.template.response import TemplateResponse


class SoloAdminSite(admin.AdminSite):
    site_header = "Soloadmin Administration"
    site_title = "Soloadmin Admin"
    index_title = "Soloadmin Panel"

    def get_urls(self):
        """Özel admin site için ek URL'ler tanımlıyoruz."""
        urls = super().get_urls()
        custom_urls = [
            path('docs/', self.admin_view(self.docs_view), name='docs'),
        ]
        return custom_urls + urls

    def docs_view(self, request):
        """
        /admin/docs/ -> Tüm Swagger ve ReDoc linklerini listeleyebilir.
        base_site.html'ü override ettiğimiz için, sol menüde de 'Docs' linki gözükecek.
        Bu sayfa docs_template.html ile renderlanır.
        """
        # Burada projenizdeki tüm swagger/redoc linklerini ekleyin
        swagger_links = [
            ("SoloAccounting Swagger", "/swagger/soloaccounting/"),
            ("SoloBlog Swagger", "/swagger/soloblog/"),
            ("SoloEcommerce Swagger", "/swagger/soloecommerce/"),
            ("SoloFinance Swagger", "/swagger/solofinance/"),
            ("SoloInvoice Swagger", "/swagger/soloinvoice/"),
            ("SoloPayment Swagger", "/swagger/solopayment/"),
            ("SoloService Swagger", "/swagger/soloservice/"),
            ("SoloWeb Swagger", "/swagger/soloweb/"),
            ("Common Swagger", "/swagger/common/"),
            ("SoloSurvey Swagger", "/swagger/solosurvey/"),
            ("SoloSite Swagger", "/swagger/solosite/"),
        ]

        redoc_links = [
            ("SoloAccounting ReDoc", "/redoc/soloaccounting/"),
            ("SoloBlog ReDoc", "/redoc/soloblog/"),
            ("SoloEcommerce ReDoc", "/redoc/soloecommerce/"),
            ("SoloFinance ReDoc", "/redoc/solofinance/"),
            ("SoloInvoice ReDoc", "/redoc/soloinvoice/"),
            ("SoloPayment ReDoc", "/redoc/solopayment/"),
            ("SoloService ReDoc", "/redoc/soloservice/"),
            ("SoloWeb ReDoc", "/redoc/soloweb/"),
            ("Common ReDoc", "/redoc/common/"),
            ("SoloSurvey ReDoc", "/redoc/solosurvey/"),
            ("SoloSite ReDoc", "/redoc/solosite/"),
        ]

        context = {
            "app_list": self.get_app_list(request),  # Admin menüde app listesi
            "swagger_links": swagger_links,
            "redoc_links": redoc_links,
        }
        return TemplateResponse(request, "admin/docs_template.html", context)


# Global bir AdminSite nesnesi
solo_admin_site = SoloAdminSite(name='soloadmin_admin')

# Tüm mevcut modelleri yeni siteye kopyalamak (böylece admin.site'da ne varsa burada da göreceğiz)
for model, model_admin in admin.site._registry.items():
    solo_admin_site._registry[model] = model_admin
