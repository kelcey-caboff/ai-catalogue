from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("catalogue", "0002_remove_usecase_tool_usecase_tools"),
    ]

    operations = [
        migrations.AddField(
            model_name="aimodel",
            name="ardoq_link",
            field=models.URLField(blank=True, help_text="Link to record in Ardoq"),
        ),
        migrations.AddField(
            model_name="aimodel",
            name="informatica_link",
            field=models.URLField(blank=True, help_text="Link to dataset in Informatica"),
        ),
        migrations.AddField(
            model_name="aimodel",
            name="contract_link",
            field=models.URLField(blank=True, help_text="Link to contract in Atamis"),
        ),
    ]
