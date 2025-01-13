# soloblog/management/commands/model_to_json.py

import os
import json

from django.core.management.base import BaseCommand
from django.apps import apps
from django.db import models

# Windows'taki kayıt dizini
OUTPUT_DIR = r"C:\Projeler\react\next-js\codegenerator\json"


class Command(BaseCommand):
    help = (
        "Kullanıcı dostu CLI ile, mevcut INSTALLED_APPS içinden uygulama ve model seçtirerek, "
        "modelin alanlarını JSON'a çıkarır. ForeignKey alanları için label/valueField bilgisi sorulur."
    )

    def handle(self, *args, **options):
        """
        1) INSTALLED_APPS içindeki uygulamaları sayıyla listele.
        2) Seçilen uygulamadaki modelleri sayıyla listele.
        3) Seçilen modelin alanlarını oku. ForeignKey için label/value sor.
        4) JSON dosyasını C:\\Projeler\\react\\next-js\\codegenerator\\json dizinine kaydet.
        """
        # 1) INSTALLED_APPS içindeki "gerçek" uygulamaları alalım.
        #    Bazı Django default app'ler de olabilir, isterseniz burayı filtreleyebilirsiniz.
        all_app_configs = apps.get_app_configs()
        all_app_labels = [app_config.label for app_config in all_app_configs]

        # Uygulamaları listele
        self.stdout.write(self.style.SUCCESS("Mevcut uygulamalar:"))
        for i, label in enumerate(all_app_labels, start=1):
            self.stdout.write(f"{i}) {label}")

        # Kullanıcıdan sayı ile seçim
        chosen_app_index = self._ask_for_index(
            prompt="Hangi uygulamayı seçmek istiyorsunuz (sayı)? ",
            max_val=len(all_app_labels),
        )
        chosen_app_label = all_app_labels[chosen_app_index - 1]

        # 2) Seçilen uygulamadaki modelleri alalım
        chosen_app_config = apps.get_app_config(chosen_app_label)
        all_models = chosen_app_config.get_models()

        # Model adlarını topluyoruz
        model_names = [m.__name__ for m in all_models]
        if not model_names:
            self.stdout.write(self.style.ERROR(f"'{chosen_app_label}' uygulamasında model bulunamadı."))
            return

        self.stdout.write(self.style.SUCCESS(f"\n'{chosen_app_label}' içindeki modeller:"))
        for i, model_name in enumerate(model_names, start=1):
            self.stdout.write(f"{i}) {model_name}")

        chosen_model_index = self._ask_for_index(
            prompt="Hangi modeli seçmek istiyorsunuz (sayı)? ",
            max_val=len(model_names),
        )
        chosen_model_name = model_names[chosen_model_index - 1]
        model = apps.get_model(chosen_app_label, chosen_model_name)

        # 3) Modelin alanlarını oku, foreignKey için label/value sor
        fields_info = []

        for field in model._meta.fields:
            field_name = field.name
            field_type = type(field).__name__
            is_required = not field.blank and not field.null
            max_length = getattr(field, 'max_length', None)

            field_dict = {
                'name': field_name,
                'type': field_type,
                'required': is_required,
                'maxLength': max_length,
            }

            # ForeignKey kontrolü
            if isinstance(field, models.ForeignKey):
                related_model = field.remote_field.model
                # İlişkili modelin alan adlarını toplayalım
                related_fields = [f.name for f in related_model._meta.fields]

                self.stdout.write(self.style.WARNING(
                    f"\n[ForeignKey] {chosen_model_name}.{field_name} --> "
                    f"{related_model._meta.app_label}.{related_model.__name__}"
                ))
                # Label field seçimi
                label_index = self._ask_for_field_choice(
                    prompt="Label olarak hangi alanı kullanmak istersiniz?",
                    field_list=related_fields,
                )
                label_field_for_fk = related_fields[label_index - 1]

                # Value field seçimi
                value_index = self._ask_for_field_choice(
                    prompt="Value olarak hangi alanı kullanmak istersiniz?",
                    field_list=related_fields,
                )
                value_field_for_fk = related_fields[value_index - 1]

                field_dict["foreignKeyLabel"] = label_field_for_fk
                field_dict["foreignKeyValue"] = value_field_for_fk

            fields_info.append(field_dict)

        output_data = {
            'app': chosen_app_label,
            'model': chosen_model_name,
            'fields': fields_info,
        }

        # 4) JSON'u diske yaz
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        output_filename = f"{chosen_app_label}_{chosen_model_name}.json"
        output_path = os.path.join(OUTPUT_DIR, output_filename)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)

        self.stdout.write(self.style.SUCCESS(
            f"\nJSON dosyası oluşturuldu: {output_path}"
        ))

    def _ask_for_index(self, prompt, max_val):
        """Kullanıcıdan 1..max_val arasında bir sayı ister, geçerli sayı girilene kadar sorar."""
        while True:
            val = input(prompt).strip()
            if val.isdigit():
                num = int(val)
                if 1 <= num <= max_val:
                    return num
            self.stdout.write(self.style.ERROR(
                f"Lütfen 1 ile {max_val} arasında geçerli bir sayı giriniz."
            ))

    def _ask_for_field_choice(self, prompt, field_list):
        """field_list içerisinden bir alan seçtirmek için kullanıcıdan sayı alır."""
        self.stdout.write(self.style.SUCCESS(prompt))
        for i, field_name in enumerate(field_list, start=1):
            self.stdout.write(f"  {i}) {field_name}")
        choice = self._ask_for_index(
            prompt="Seçiminiz (sayı): ",
            max_val=len(field_list)
        )
        return choice
