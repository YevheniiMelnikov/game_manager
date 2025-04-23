from django.db import migrations, models
import django.contrib.auth.models
import django.utils.timezone
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = []  # type: ignore

    operations = [
        migrations.CreateModel(
            name="Company",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=255, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name="CustomUser",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("password", models.CharField(max_length=128, verbose_name="password")),
                ("last_login", models.DateTimeField(blank=True, null=True, verbose_name="last login")),
                ("is_superuser", models.BooleanField(default=False)),
                ("username", models.CharField(max_length=150, unique=True)),
                ("first_name", models.CharField(blank=True, max_length=150)),
                ("last_name", models.CharField(blank=True, max_length=150)),
                ("email", models.EmailField(blank=True, max_length=254)),
                ("is_staff", models.BooleanField(default=False)),
                ("is_active", models.BooleanField(default=True)),
                ("date_joined", models.DateTimeField(default=django.utils.timezone.now)),
                ("role", models.CharField(default="Participant", max_length=20)),
                (
                    "company",
                    models.ForeignKey(
                        blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to="games.company"
                    ),
                ),
            ],
            options={"abstract": False},
            managers=[("objects", django.contrib.auth.models.UserManager())],
        ),
        migrations.CreateModel(
            name="Game",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=255)),
                ("language", models.CharField(max_length=50)),
                ("category", models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name="GameSession",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("start_datetime", models.DateTimeField()),
                ("status", models.CharField(max_length=20)),
                ("game", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="games.game")),
                ("participants", models.ManyToManyField(related_name="game_sessions", to="games.CustomUser")),
            ],
        ),
        migrations.CreateModel(
            name="GameResults",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("score", models.IntegerField()),
                ("is_completed", models.BooleanField()),
                (
                    "game_session",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE, related_name="results", to="games.gamesession"
                    ),
                ),
            ],
        ),
    ]
