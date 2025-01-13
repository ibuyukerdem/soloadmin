from django.contrib import admin
from .models import Survey, Question, Choice, SurveyTrigger, SurveyResponse, Answer

class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 2
    verbose_name = "Seçenek"
    verbose_name_plural = "Seçenekler"
    # Bu inline özellikle Çoksan Seçmeli sorular için soruların altında seçenek eklemeyi kolaylaştırır.
    fields = ("choiceText",)
    readonly_fields = ()
    show_change_link = True

class QuestionInline(admin.StackedInline):
    model = Question
    extra = 1
    verbose_name = "Soru"
    verbose_name_plural = "Sorular"
    # Alanlar ve help_text otomatik olarak modelden gelir
    fields = ("questionText", "questionType")
    show_change_link = True
    inlines = [ChoiceInline]

@admin.register(Survey)
class SurveyAdmin(admin.ModelAdmin):
    list_display = ("title", "site", "isActive", "startDate", "endDate", "rewardPoints", "createdAt")
    list_filter = ("site", "isActive", "startDate", "endDate")
    search_fields = ("title", "description", "site__domain")
    date_hierarchy = "startDate"
    inlines = [QuestionInline]
    fieldsets = (
        (None, {
            "fields": (
                "site",
                "title",
                "description"
            ),
            "description": "Anketin temel bilgilerini burada ayarlayabilirsiniz."
        }),
        ("Zaman ve Durum", {
            "fields": ("startDate", "endDate", "isActive"),
            "description": "Anketin aktif olduğu dönemi ve aktif/pasif durumunu ayarlayın."
        }),
        ("Ödül Ayarları", {
            "fields": ("rewardPoints",),
            "description": "Anketi dolduran kullanıcılara verilecek ödül puanını tanımlayın."
        }),
    )
    # Otomatik tarih alanları admin'de otomatik yansıyacaktır.

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("questionText", "survey", "questionType", "createdAt")
    list_filter = ("questionType", "survey__site")
    search_fields = ("questionText", "survey__title")
    inlines = [ChoiceInline]
    fieldsets = (
        (None, {
            "fields": ("site", "survey", "questionText", "questionType"),
            "description": "Soru metni ve tipini burada düzenleyin. Çoktan seçmeli sorular için seçenekleri alt kısımdan ekleyin."
        }),
    )

@admin.register(Choice)
class ChoiceAdmin(admin.ModelAdmin):
    list_display = ("choiceText", "question", "createdAt")
    search_fields = ("choiceText", "question__questionText")
    fieldsets = (
        (None, {
            "fields": ("site", "question", "choiceText"),
            "description": "Bu seçenek ilgili soruya ait olacak şekilde tanımlanır."
        }),
    )

@admin.register(SurveyTrigger)
class SurveyTriggerAdmin(admin.ModelAdmin):
    list_display = ("survey", "triggerEvent", "sendEmail", "sendSms", "sendWhatsapp", "delayHours", "createdAt")
    list_filter = ("survey__site", "triggerEvent", "sendEmail", "sendSms", "sendWhatsapp")
    search_fields = ("survey__title", "triggerEvent")
    fieldsets = (
        (None, {
            "fields": ("site", "survey", "triggerEvent"),
            "description": "Anketi hangi olay veya koşuldan sonra tetiklemek istediğinizi belirleyin."
        }),
        ("Bildirim Ayarları", {
            "fields": ("sendEmail", "sendSms", "sendWhatsapp", "delayHours"),
            "description": "Tetikleme sonrasında hangi kanallardan ve ne kadar gecikmeli olarak anket gönderileceğini ayarlayın."
        }),
    )

class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 0
    verbose_name = "Cevap"
    verbose_name_plural = "Cevaplar"
    fields = ("question", "answerText", "selectedChoice", "numericValue")
    readonly_fields = ("question",)
    show_change_link = False
    can_delete = False

@admin.register(SurveyResponse)
class SurveyResponseAdmin(admin.ModelAdmin):
    list_display = ("survey", "respondent", "anonymousIdentifier", "completedAt")
    list_filter = ("survey__site", "survey__title", "respondent")
    search_fields = ("survey__title", "respondent__username", "anonymousIdentifier")
    date_hierarchy = "completedAt"
    inlines = [AnswerInline]
    fieldsets = (
        (None, {
            "fields": ("site", "survey", "respondent", "anonymousIdentifier"),
            "description": "Anket yanıtını hangi kullanıcı ya da anonim katılımcı doldurduğunu gösterir."
        }),
        ("Zaman Bilgisi", {
            "fields": ("completedAt",),
            "description": "Anketin doldurulduğu tarih."
        }),
    )
    readonly_fields = ("completedAt",)

@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ("response", "question", "answerText", "selectedChoice", "numericValue", "createdAt")
    list_filter = ("response__survey__site", "question__survey__title")
    search_fields = ("question__questionText", "answerText", "selectedChoice__choiceText")
    fieldsets = (
        (None, {
            "fields": ("site", "response", "question", "answerText", "selectedChoice", "numericValue"),
            "description": "Bu yanıt belirli bir soru için verilmiştir. Text veya seçilen seçenek bilgilerinin yanı sıra sayısal puan da görüntülenebilir."
        }),
    )
    readonly_fields = ("response", "question")
