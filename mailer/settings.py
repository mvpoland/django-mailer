from django.conf import settings


""" Add here dictionary of extra headers pushed forward to django's EmailMultiAlternatives and EmailMessage.

Example:
    to activate click and open action for e-mails sent by Mandrillapp you'll need to define this as follows:

    MAIL_EXTRA_HEADERS = {'X-MC-Track': 'opens,clicks'}

"""
MAILER_EXTRA_HEADERS = getattr(settings, 'MAILER_EXTRA_HEADERS', None)


""" Python path for scheduler class that will do the job to put message right after being created
    onto your queue mechanism. 

Normally this package will do the job using management command, but you could use different mechanism
like celery if you need to using this setting.

Example:

    ```
    class BasicCeleryScheduler(object):
        def schedule(self, message):
            if message.priority == PRIORITY_MAPPING['high']:
                send_mail_job.apply_async(message.id, queue='mailer.priority.high')
            else:
                send_mail_job.apply_async(message.id, queue='mailer.other')
    ```
"""
MAILER_SCHEDULER = getattr(settings, 'MAILER_SCHEDULER', False)
