# Generated by Django 3.2.9 on 2021-11-28 05:41

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('description', models.CharField(max_length=200)),
                ('image', models.ImageField(upload_to='images/')),
            ],
        ),
        migrations.CreateModel(
            name='Offers',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='images/')),
            ],
        ),
        migrations.CreateModel(
            name='product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Name', models.CharField(max_length=100)),
                ('Brand', models.CharField(max_length=100)),
                ('Category', models.CharField(max_length=100)),
                ('category_name', models.CharField(max_length=100)),
                ('per_unit', models.CharField(max_length=100)),
                ('Qty', models.IntegerField()),
                ('Rate', models.IntegerField()),
                ('Discount', models.IntegerField()),
                ('Percentage', models.IntegerField()),
                ('Total_rate', models.IntegerField()),
                ('Top_product', models.CharField(max_length=20)),
                ('Image', models.ImageField(blank=True, null=True, upload_to='images')),
            ],
        ),
        migrations.CreateModel(
            name='product_images',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Product_id', models.CharField(max_length=10)),
                ('Image_path', models.ImageField(blank=True, null=True, upload_to='images')),
            ],
        ),
        migrations.CreateModel(
            name='UserDetails',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('full_name', models.CharField(blank=True, max_length=100, null=True)),
                ('username', models.CharField(max_length=100, unique=True)),
                ('user_email', models.EmailField(max_length=254, unique=True)),
                ('password', models.CharField(max_length=8)),
                ('address', models.CharField(blank=True, max_length=250, null=True)),
                ('mobile', models.CharField(max_length=12)),
                ('image', models.ImageField(upload_to='images')),
            ],
        ),
        migrations.CreateModel(
            name='My_order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('User_id', models.IntegerField()),
                ('Product_name', models.CharField(max_length=200)),
                ('Brand', models.CharField(max_length=200)),
                ('Category', models.CharField(max_length=200)),
                ('Qty_count', models.CharField(max_length=200)),
                ('Rate', models.IntegerField()),
                ('Discount', models.IntegerField()),
                ('Total_rate', models.IntegerField()),
                ('Status', models.CharField(max_length=100)),
                ('Message', models.CharField(max_length=240)),
                ('Booking_address', models.CharField(max_length=240)),
                ('datetime', models.DateTimeField(auto_now=True)),
                ('Product', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='arman.product')),
            ],
        ),
        migrations.CreateModel(
            name='Cart',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('User_id', models.IntegerField()),
                ('Qty_count', models.IntegerField()),
                ('Rate', models.IntegerField()),
                ('Discount', models.IntegerField()),
                ('Total_rate', models.IntegerField()),
                ('Product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='arman.product')),
            ],
        ),
        migrations.CreateModel(
            name='AdminDetails',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Mobile', models.CharField(max_length=12)),
                ('Image', models.ImageField(blank=True, upload_to='images')),
                ('Address', models.CharField(blank=True, max_length=250, null=True)),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
