from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings

def send_overdue_notification_email(membership, book_title, due_date):
    full_name = membership.member.full_name
    recipient_email = membership.member.email
    email_subject = 'Book Overdue Notification'
    email_body = render_to_string('overdue_email.html', {
        'full_name': full_name,
        'book_title': book_title,
        'due_date': due_date,
    })
    send_mail(
        email_subject,
        '',
        settings.EMAIL_HOST_USER,
        [recipient_email],
        html_message=email_body,
        fail_silently=False
    )