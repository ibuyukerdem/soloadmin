from django.core.files.uploadedfile import InMemoryUploadedFile
from rest_framework.exceptions import PermissionDenied
from rest_framework.viewsets import ModelViewSet

from common.utils.logging_helper import log_action


class AbstractBaseViewSet(ModelViewSet):
    """
    Gelişmiş Soyut ViewSet Sınıfı:
    - Kullanıcının `selectedSite` alanına göre işlemler yapmasını sağlar.
    - CRUD işlemleri sırasında loglama yapılır.
    - Yeni kayıt oluştururken site bilgisi `selectedSite` üzerinden otomatik atanır.
    """

    def validate_user_site(self):
        """
        Kullanıcının seçili siteye (selectedSite) erişim yetkisini kontrol eder.
        """
        user = self.request.user
        if not user.is_authenticated:
            raise PermissionDenied("Kullanıcı oturum açmamış.")

        if not user.selectedSite:
            raise PermissionDenied("Seçili bir siteniz bulunmuyor. Lütfen bir site seçin.")

    def get_queryset(self):
        """
        Kullanıcının seçili sitesi baz alınarak sorgu kümesini filtreler.
        """
        self.validate_user_site()
        queryset = super().get_queryset()
        return queryset.filter(site=self.request.user.selectedSite)

    def perform_create(self, serializer):
        """
        Yeni bir kayıt oluşturulurken:
        - Kullanıcının seçili site bilgisi (selectedSite) doğrulanır.
        - Site bilgisi otomatik atanır.
        """
        user = self.request.user
        self.validate_user_site()  # Kullanıcının yetkisini doğrula

        # Site bilgisi otomatik atanır
        serializer.save(site=user.selectedSite)

    def perform_update(self, serializer):
        """
        Bir kaydı güncellerken kullanıcının yetkili olduğunu doğrular.
        """
        self.validate_user_site()
        super().perform_update(serializer)

    def perform_destroy(self, instance):
        """
        Bir kaydı silerken kullanıcının yetkili olduğunu doğrular.
        """
        self.validate_user_site()
        super().perform_destroy(instance)

    def _clean_data_for_logging(self, data):
        """
        Gelen verilerin içinde yer alan InMemoryUploadedFile (yani dosya)
        nesnelerini JSON uyumlu hale getirmek veya tamamen çıkartmak için kullanılır.
        """

        # request.data çoğunlukla QueryDict olabileceği için .items() ile itere edilir
        # veya normal dict ise yine .items() uyumlu
        if hasattr(data, 'items'):
            items = data.items()
        else:
            items = data.items()  # normal dict ise de çalışır

        cleaned_data = {}
        for key, value in items:
            if isinstance(value, InMemoryUploadedFile):
                # Dosya nesnesini logdan tamamen çıkarabilir
                # veya sadece dosya adını saklayabilirsiniz. Ör: value.name
                cleaned_data[key] = f"<file_excluded:{value.name}>"
            else:
                cleaned_data[key] = value

        return cleaned_data

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)

        cleaned_data = self._clean_data_for_logging(request.data)
        log_action(
            request=request,
            model_name=self.get_queryset().model.__name__,
            operation="CREATE",
            data=cleaned_data,  # Dosya alanları çıkarılmış veri
            site=request.user.selectedSite
        )
        return response

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)

        cleaned_data = self._clean_data_for_logging(request.data)
        log_action(
            request=request,
            model_name=self.get_queryset().model.__name__,
            operation="UPDATE",
            data=cleaned_data,
            site=request.user.selectedSite
        )
        return response

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        response = super().destroy(request, *args, **kwargs)

        # Silme işleminde sadece ID bilgisini kaydederiz.
        # İsterseniz burada da request.data yerine ekstra alanları temizleyebilirsiniz.
        log_action(
            request=request,
            model_name=self.get_queryset().model.__name__,
            operation="DELETE",
            data={"id": instance.id},
            site=request.user.selectedSite
        )
        return response
