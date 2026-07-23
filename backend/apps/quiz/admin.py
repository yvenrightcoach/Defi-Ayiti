from django.contrib import admin

from .models import Answer, Category, Question


class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 4
    fields = ("text", "image", "is_correct", "order")


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "order")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("__str__", "category", "question_type", "difficulty", "is_boss_question", "is_active")
    list_filter = ("category", "question_type", "difficulty", "is_boss_question", "is_active")
    search_fields = ("text",)
    autocomplete_fields = ("category", "department", "level")
    inlines = [AnswerInline]


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ("question", "text", "is_correct", "order")
    list_filter = ("is_correct",)
    search_fields = ("text", "question__text")
    autocomplete_fields = ("question",)
