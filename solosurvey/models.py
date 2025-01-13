from django.db import models
from django.contrib.sites.models import Site
from django.conf import settings
from common.models import AbstractBaseModel


class Survey(AbstractBaseModel):
    """
    Belirli bir siteye bağlı olarak oluşturulan anket modeli.
    """
    title = models.CharField(max_length=255, verbose_name="Anket Başlığı")
    description = models.TextField(verbose_name="Anket Açıklaması", blank=True, null=True)
    startDate = models.DateTimeField(verbose_name="Başlangıç Tarihi", null=True, blank=True)
    endDate = models.DateTimeField(verbose_name="Bitiş Tarihi", null=True, blank=True)
    isActive = models.BooleanField(default=True, verbose_name="Aktif Mi?")
    rewardPoints = models.PositiveIntegerField(default=0, verbose_name="Ödül Puanı")

    # Örn: Anket doldurana verilecek puan. İleride kullanıcıya ödül sistemine entegre edilebilir.

    class Meta:
        verbose_name = "Anket"
        verbose_name_plural = "Anketler"
        db_table = "solosurvey_surveys"

    def __str__(self):
        return f"{self.site.domain} - {self.title}"


class Question(AbstractBaseModel):
    """
    Anket soruları. Her soru bir ankete ait.
    questionType örn: "text", "rating", "multiple_choice", "single_choice"
    """
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, related_name="questions")
    questionText = models.TextField(verbose_name="Soru Metni")
    questionType = models.CharField(
        max_length=50,
        choices=[
            ("text", "Metin Yanıt"),
            ("rating", "Puanlama"),
            ("multiple_choice", "Çoktan Seçmeli"),
            ("single_choice", "Tek Seçimli"),
        ],
        default="text",
        verbose_name="Soru Tipi"
    )

    class Meta:
        verbose_name = "Soru"
        verbose_name_plural = "Sorular"
        db_table = "solosurvey_questions"

    def __str__(self):
        return f"{self.survey.title} - {self.questionText[:50]}"


class Choice(AbstractBaseModel):
    """
    Çoktan seçmeli sorular için seçenekler.
    """
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="choices")
    choiceText = models.CharField(max_length=255, verbose_name="Seçenek Metni")

    class Meta:
        verbose_name = "Seçenek"
        verbose_name_plural = "Seçenekler"
        db_table = "solosurvey_choices"

    def __str__(self):
        return f"{self.question.questionText[:50]} - {self.choiceText}"


class SurveyTrigger(AbstractBaseModel):
    """
    Anketin hangi durumda tetikleneceğini belirten model.
    Örneğin: Belirli bir sipariş tamamlandığında müşteriye mail ile anket gönderimi.
    """
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, related_name="triggers")
    triggerEvent = models.CharField(max_length=255, verbose_name="Tetikleyici Olay")
    # triggerEvent örn: "order_completed", "support_ticket_closed", vb.
    sendEmail = models.BooleanField(default=False, verbose_name="E-posta Gönder?")
    sendSms = models.BooleanField(default=False, verbose_name="SMS Gönder?")
    sendWhatsapp = models.BooleanField(default=False, verbose_name="WhatsApp Mesajı Gönder?")
    # Zamanlama seçenekleri, örn: "Hemen", "1 gün sonra", vb.
    delayHours = models.PositiveIntegerField(default=0, verbose_name="Gönderim Gecikmesi (saat)")

    class Meta:
        verbose_name = "Anket Tetikleyici"
        verbose_name_plural = "Anket Tetikleyiciler"
        db_table = "solosurvey_triggers"

    def __str__(self):
        return f"{self.survey.title} - {self.triggerEvent}"


class SurveyResponse(AbstractBaseModel):
    """
    Anketin kullanıcı veya anonim katılımcı tarafından doldurulması.
    """
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, related_name="responses")
    respondent = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        verbose_name="Cevaplayan Kullanıcı"
    )
    # anonim kullanıcılarda email veya başka bir tanımlayıcı tutulabilir.
    anonymousIdentifier = models.CharField(max_length=255, blank=True, null=True, verbose_name="Anonim Kimlik")

    completedAt = models.DateTimeField(auto_now_add=True, verbose_name="Tamamlanma Tarihi")

    class Meta:
        verbose_name = "Anket Yanıtı"
        verbose_name_plural = "Anket Yanıtları"
        db_table = "solosurvey_responses"

    def __str__(self):
        return f"{self.survey.title} yanıtı - {self.respondent or self.anonymousIdentifier}"


class Answer(AbstractBaseModel):
    """
    Bir SurveyResponse içindeki soru-cevap eşleştirmesi.
    """
    response = models.ForeignKey(SurveyResponse, on_delete=models.CASCADE, related_name="answers")
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answerText = models.TextField(blank=True, null=True, verbose_name="Metin Yanıt")
    selectedChoice = models.ForeignKey(
        Choice,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="selected_answers",
        verbose_name="Seçilen Seçenek"
    )
    numericValue = models.IntegerField(null=True, blank=True, verbose_name="Sayısal Değer (örn. rating)")

    class Meta:
        verbose_name = "Cevap"
        verbose_name_plural = "Cevaplar"
        db_table = "solosurvey_answers"

    def __str__(self):
        return f"{self.question.questionText[:50]} - {self.answerText or self.selectedChoice or self.numericValue}"
