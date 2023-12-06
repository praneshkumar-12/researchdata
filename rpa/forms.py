from django import forms
from rpa.models import Publications


class PublicationsForm(forms.ModelForm):
    class Meta:
        model = Publications
        fields = [
            "title",
            "first_author",
            "second_author",
            "third_author",
            "other_authors",
            "is_student_author",
            "student_name",
            "student_batch",
            "specification",
            "publication_type",
            "publication_name",
            "publisher",
            "year_of_publishing",
            "month_of_publishing",
            "volume",
            "page_number",
            "indexing",
            "quartile",
            "citation",
            "doi",
            "front_page_path",
            "url",
            "issn",
        ]
        # fields = [f for f in Publications._meta.get_fields()]
