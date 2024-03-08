from django.db import models


class Publications(models.Model):
    uniqueid = models.CharField(primary_key=True, max_length=100)
    title = models.CharField(max_length=500)
    start_academic_month = models.CharField(max_length=10, blank=True, null=True)
    start_academic_year = models.IntegerField(
        blank=True, null=True
    )  # This field type is a guess.
    end_academic_month = models.CharField(max_length=10, blank=True, null=True)
    end_academic_year = models.IntegerField(
        blank=True, null=True
    )  # This field type is a guess.
    first_author = models.CharField(max_length=50)
    second_author = models.CharField(max_length=50, blank=True, null=True)
    third_author = models.CharField(max_length=50, blank=True, null=True)
    other_authors = models.CharField(max_length=500, blank=True, null=True)
    is_student_author = models.CharField(max_length=10, blank=True, null=True)
    student_name = models.CharField(max_length=50, blank=True, null=True)
    student_batch = models.CharField(max_length=10, blank=True, null=True)
    specification = models.CharField(max_length=30, blank=True, null=True)
    publication_type = models.CharField(max_length=30, blank=True, null=True)
    publication_name = models.CharField(max_length=500, blank=True, null=True)
    publisher = models.CharField(max_length=500, blank=True, null=True)
    year_of_publishing = models.IntegerField(
        blank=True, null=True
    )  # This field type is a guess.
    month_of_publishing = models.CharField(max_length=10, blank=True, null=True)
    volume = models.IntegerField(blank=True, null=True, default=0)
    page_number = models.CharField(max_length=100, blank=True, null=True)
    indexing = models.CharField(max_length=100, blank=True, null=True)
    quartile = models.CharField(max_length=10, blank=True, null=True)
    citation = models.IntegerField(blank=True, null=True, default=0)
    doi = models.CharField(max_length=255, blank=True, null=True, unique=True)
    front_page_path = models.CharField(max_length=500, blank=True, null=True)
    url = models.CharField(max_length=500, blank=True, null=True)
    issn = models.CharField(
        db_column="ISSN", max_length=500, blank=True, null=True
    )  # Field name made lowercase.
    verified = models.CharField(max_length=10, blank=True, null=True, default="False")
    admin_verified = models.CharField(
        max_length=10, blank=True, null=True, default="False"
    )

    class Meta:
        managed = False
        db_table = "publications"


class Users(models.Model):
    author_id = models.CharField(primary_key=True, max_length=35)
    email_id = models.CharField(max_length=35, blank=True, null=True)
    staff_name = models.CharField(max_length=50, blank=True, null=True)
    passkey = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = "users"


class AdminUsers(models.Model):
    email_id = models.CharField(primary_key=True, max_length=35, blank=True)
    staff_name = models.CharField(max_length=50, blank=True, null=True)
    passkey = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = "adminusers"
