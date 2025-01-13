from django.core.management.base import BaseCommand
from faker import Faker
import random
from django.utils.text import slugify
from django.utils import timezone

from django.contrib.sites.models import Site
from soloblog.models import Category, Article, Image, Comment

class Command(BaseCommand):
    help = 'Generate fake Turkish data with placeholder images (no disk save) for Sites with ID 3..6'

    def handle(self, *args, **options):
        fake = Faker('tr_TR')

        # Sadece ID'si 3 ile 6 arasında olan siteleri seçiyoruz
        sites = Site.objects.filter(id__range=(3, 6))

        for site in sites:
            self.stdout.write(self.style.WARNING(
                f"--- İşlem başlıyor: {site.domain} (ID: {site.id}) ---"
            ))

            # 1) 10 adet kategori oluştur
            categories = []
            for _ in range(10):
                category_name = fake.word()  # ör. "masa", "kitap" vb. Türkçe kelime
                cat_slug = f"{slugify(category_name)}-{fake.random_int(min=1, max=999999)}"

                category = Category.objects.create(
                    site=site,
                    categoryName=category_name.title(),
                    categoryDescription=fake.paragraph(nb_sentences=3),
                    slug=cat_slug,
                    meta=fake.sentence(nb_words=6),
                    metaDescription=fake.sentence(nb_words=8),
                )
                categories.append(category)

            self.stdout.write(self.style.SUCCESS(f"  --> {len(categories)} kategori eklendi."))

            # 2) 5000 adet makale oluştur
            total_articles = 5000
            article_count = 0

            for i in range(total_articles):
                category = random.choice(categories)
                title = fake.sentence(nb_words=6)
                article_slug = f"{slugify(title)}-{fake.random_int(min=1, max=999999)}"

                article = Article.objects.create(
                    site=site,
                    category=category,
                    title=title,
                    content=fake.paragraph(nb_sentences=10),
                    slug=article_slug,
                    meta=fake.sentence(nb_words=6),
                    metaDescription=fake.sentence(nb_words=8),
                    publicationDate=fake.date_time_between(
                        start_date='-1y',
                        end_date='now',
                        tzinfo=timezone.get_current_timezone()
                    ),
                )

                # 3) Her makale için 5 adet placeholder resim
                for _ in range(5):
                    image = self._create_placeholder_image(article)
                    image.save()

                # 4) Her makale için 10 adet yorum
                for _ in range(10):
                    Comment.objects.create(
                        site=site,
                        article=article,
                        approved=random.choice([True, False]),
                        firstName=fake.first_name(),
                        lastName=fake.last_name(),
                        email=fake.email(),
                        phoneNumber=fake.phone_number(),
                        rating=random.randint(1, 5),
                        content=fake.paragraph(nb_sentences=3),
                        ip=fake.ipv4(),
                    )

                article_count += 1
                if article_count % 100 == 0:
                    self.stdout.write(f"  --> {article_count} makale oluşturuldu...")

            self.stdout.write(self.style.SUCCESS(
                f"{site.domain} için toplam {article_count} makale eklendi."
            ))

        self.stdout.write(self.style.SUCCESS("Tüm işlemler tamamlandı."))

    def _create_placeholder_image(self, article):
        """
        Diske kaydetmek yerine, 'imagePath' alanına doğrudan
        placeholder URL atayan yardımcı fonksiyon.
        """
        # İstediğiniz boyutu / tipi değiştirebilirsiniz:
        placeholder_url = "https://via.placeholder.com/600x400.png"

        # Image modeli örneği oluşturalım
        image_instance = Image(
            site=article.site,
            article=article
        )
        # Normalde .save() ile dosya yüklenir, fakat biz fiziksel bir dosya yok;
        # direkt name alanına URL veriyoruz.
        # Bu sayede veritabanına "imagePath" = "https://..." kaydedilecek.
        image_instance.imagePath.name = placeholder_url

        return image_instance
