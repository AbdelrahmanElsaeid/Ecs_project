
# Create your models here.
import math
from random import SystemRandom
import string

from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

from src.users.utils import get_full_name
from src.core.models import EthicsCommission


PASSPHRASE_ENTROPY = 80
PASSPHRASE_CHARS = string.ascii_lowercase + string.digits


class Certificate(models.Model):
    user = models.ForeignKey(User, related_name='certificates', on_delete=models.CASCADE)
    cn = models.CharField(max_length=64, unique=True)
    subject = models.TextField()
    serial = models.IntegerField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    revoked_at = models.DateTimeField(null=True)

    @classmethod
    def get_serial(cls):
        last_serial = cls.objects.aggregate(models.Max('serial'))['serial__max']
        return (last_serial or 0) + 1

    @classmethod
    def get_crlnumber(cls):
        return cls.objects.exclude(revoked_at=None).count() + 1

    @classmethod
    def create_for_user(cls, pkcs12, user, cn=None, days=None):
        if not cn:
            cn = get_full_name(user)
        try:
            ec = EthicsCommission.objects.get(uuid=settings.ETHICS_COMMISSION_UUID)
        except EthicsCommission.DoesNotExist:
            # Handle the case when the object does not exist (e.g., create a new one)
            ec = EthicsCommission()
        # ec = EthicsCommission.objects.get(uuid=settings.ETHICS_COMMISSION_UUID)
        subject = '/CN={}/O={}/emailAddress={}'.format(cn, ec.name[:64], user.email)

        passphrase_len = math.ceil(
            PASSPHRASE_ENTROPY / math.log2(len(PASSPHRASE_CHARS)))
        passphrase = ''.join(
            SystemRandom().choice(PASSPHRASE_CHARS)
            for i in range(passphrase_len)
        )

        from src.pki.openssl import make_cert
        data = make_cert(subject, pkcs12, passphrase=passphrase,
            days=days)
        cert = cls.objects.create(user=user, cn=cn, **data)

        return (cert, passphrase)

    @property
    def is_expired(self):
        return self.expires_at < timezone.now()

    def revoke(self):
        assert self.revoked_at is None
        self.revoked_at = timezone.now()
        self.save()

        from pki import openssl
        openssl.gen_crl()


class CertificateAuthority(models.Model):
    key = models.TextField()
    cert = models.TextField()