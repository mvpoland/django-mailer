# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Attachment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('attachment_file', models.FileField(upload_to=b'attachments/', verbose_name='attachment file', blank=True)),
                ('filename', models.CharField(max_length=255)),
                ('mimetype', models.CharField(max_length=255, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='DontSendEntry',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('to_address', models.CharField(max_length=50)),
                ('when_added', models.DateTimeField()),
            ],
            options={
                'verbose_name': "don't send entry",
                'verbose_name_plural': "don't send entries",
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('to_address', models.CharField(max_length=50)),
                ('from_address', models.CharField(max_length=50)),
                ('subject', models.CharField(max_length=100)),
                ('message_body', models.TextField()),
                ('when_added', models.DateTimeField(default=datetime.datetime.now)),
                ('priority', models.CharField(default=b'2', max_length=1, choices=[(b'1', b'high'), (b'2', b'medium'), (b'3', b'low'), (b'4', b'deferred')])),
                ('html_body', models.TextField(blank=True)),
                ('ready_to_send', models.BooleanField(default=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='MessageLog',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('to_address', models.CharField(max_length=50, db_index=True)),
                ('from_address', models.CharField(max_length=50)),
                ('subject', models.CharField(max_length=100)),
                ('message_body', models.TextField()),
                ('when_added', models.DateTimeField()),
                ('priority', models.CharField(max_length=1, choices=[(b'1', b'high'), (b'2', b'medium'), (b'3', b'low'), (b'4', b'deferred')])),
                ('html_body', models.TextField(blank=True)),
                ('when_attempted', models.DateTimeField(default=datetime.datetime.now)),
                ('result', models.CharField(max_length=1, choices=[(b'1', b'success'), (b'2', b"don't send"), (b'3', b'failure')])),
                ('log_message', models.TextField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='attachment',
            name='message',
            field=models.ForeignKey(to='mailer.Message'),
            preserve_default=True,
        ),
    ]
