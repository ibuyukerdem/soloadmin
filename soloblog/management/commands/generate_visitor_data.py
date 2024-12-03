from django.core.management.base import BaseCommand
from soloblog.models import VisitorAnalytics, Site, Category, Article
from faker import Faker
import random
from django.utils import timezone

fake = Faker('tr_TR')

class Command(BaseCommand):
    help = 'Generate fake categories, articles, and visitor analytics data'

    def handle(self, *args, **kwargs):
        sites = Site.objects.all()

        # Kategorileri oluştur
        for site in sites:
            for _ in range(50):
                Category.objects.create(
                    site=site,
                    categoryName=fake.word(),
                    categoryDescription=fake.text(),
                    slug=f'{fake.unique.slug()}-{fake.random_int(min=1, max=10000)}',
                    meta=fake.text(),
                    metaDescription=fake.text()
                )

        # Makaleleri oluştur
        categories = Category.objects.all()
        for category in categories:
            for _ in range(50):
                Article.objects.create(
                    site=category.site,
                    category=category,
                    title=fake.sentence(),
                    content=fake.text(),
                    slug=f'{fake.unique.slug()}-{fake.random_int(min=1, max=10000)}',
                    meta=fake.text(),
                    metaDescription=fake.text()
                )

        # Ziyaretçi kayıtlarını oluştur
        articles = Article.objects.all()
        visit_types = ['homepage', 'article']

        for _ in range(5000):
            site = random.choice(sites)
            visit_type = random.choice(visit_types)
            article = None
            if visit_type == 'article':
                article = random.choice(articles)

            VisitorAnalytics.objects.create(
                site=site,
                visit_type=visit_type,
                article=article,
                ip_address=fake.ipv4(),
                user_agent=fake.user_agent(),
                referer=fake.url(),
                visit_date=fake.date_time_between(start_date='-1y', end_date='now', tzinfo=timezone.now().tzinfo),
                country=fake.country(),
                city=fake.city(),
                device_type=random.choice(['mobil', 'masaüstü', 'tablet']),
                operating_system=fake.word(ext_word_list=['Windows', 'macOS', 'Linux', 'Android', 'iOS']),
                browser=fake.word(ext_word_list=['Chrome', 'Firefox', 'Safari', 'Edge', 'Opera']),
                session_duration=random.randint(10, 600),
            )

        self.stdout.write(self.style.SUCCESS('Successfully generated categories, articles, and visitor analytics records.'))
