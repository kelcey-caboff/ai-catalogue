from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("catalogue", "0003_aimodel_external_links"),
    ]

    operations = [
        migrations.AddField(
            model_name="aitool",
            name="website",
            field=models.URLField(blank=True, help_text="Public URL for the tool or product"),
        ),
    ]
