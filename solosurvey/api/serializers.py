from rest_framework import serializers
from solosurvey.models import Survey, Question, Choice, SurveyTrigger, SurveyResponse, Answer

class ChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = ["id", "choiceText"]

class QuestionSerializer(serializers.ModelSerializer):
    choices = ChoiceSerializer(many=True, read_only=True)
    class Meta:
        model = Question
        fields = ["id", "questionText", "questionType", "choices"]

class SurveySerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)
    class Meta:
        model = Survey
        fields = ["id", "title", "description", "startDate", "endDate", "isActive", "rewardPoints", "questions"]

class SurveyTriggerSerializer(serializers.ModelSerializer):
    class Meta:
        model = SurveyTrigger
        fields = ["id", "survey", "triggerEvent", "sendEmail", "sendSms", "sendWhatsapp", "delayHours"]

class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ["id", "question", "answerText", "selectedChoice", "numericValue"]

class SurveyResponseSerializer(serializers.ModelSerializer):
    answers = AnswerSerializer(many=True)
    class Meta:
        model = SurveyResponse
        fields = ["id", "survey", "respondent", "anonymousIdentifier", "completedAt", "answers"]

    def create(self, validated_data):
        answers_data = validated_data.pop("answers", [])
        response = SurveyResponse.objects.create(**validated_data)
        for ans_data in answers_data:
            Answer.objects.create(response=response, **ans_data)
        return response
