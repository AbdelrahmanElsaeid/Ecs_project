import os
from django.db import models

# Create your models here.


import tempfile
import mimetypes
import logging
import uuid

from django.conf import settings
from django.db import models
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.utils.text import slugify
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.auth.models import User
from django.utils.translation import gettext as _
from django.utils import timezone

from src.utils.pdfutils import pdf_barcodestamp
from src.documents.storagevault import getVault


logger = logging.getLogger(__name__)


class DocumentType(models.Model):
    name = models.CharField(max_length=100)
    identifier = models.CharField(max_length=30, db_index=True, blank=True, default="")
    is_hidden = models.BooleanField(default=False)
    is_downloadable = models.BooleanField(default=True)

    def __str__(self):
        return _(self.name)
    class Meta:
        app_label = 'documents'
        #abstract = True


class DocumentManager(models.Manager):
    def create_from_buffer(self, buf, **kwargs):
        if 'doctype' in kwargs and isinstance(kwargs['doctype'], str):
            kwargs['doctype'] = DocumentType.objects.get(identifier=kwargs['doctype'])

        now = timezone.now()
        kwargs.setdefault('date', now)
        kwargs.setdefault('version', str(now))

        doc = self.create(**kwargs)
        with tempfile.TemporaryFile() as f:
            f.write(buf)
            f.flush()
            f.seek(0)
            doc.store(f)
        return doc


class Document(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, unique=True)
    original_file_name = models.CharField(max_length=250, null=True, blank=True)
    mimetype = models.CharField(max_length=100, default='application/pdf')
    stamp_on_download = models.BooleanField(default=True)

    # user supplied data
    name = models.CharField(max_length=250)
    doctype = models.ForeignKey(DocumentType, on_delete=models.CASCADE)
    version = models.CharField(max_length=250)
    date = models.DateTimeField()
    replaces_document = models.ForeignKey('Document', null=True, blank=True, on_delete=models.CASCADE)

    # relation to an object
    content_type = models.ForeignKey(ContentType, null=True, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField(null=True)
    parent_object = GenericForeignKey('content_type', 'object_id')

    objects = DocumentManager()

    def __str__(self):
        t = _("Sonstige Unterlagen")
        if self.doctype_id:
            t = self.doctype.name
        return '{} {}-{} vom {}'.format(t, self.name, self.version,
                                         timezone.localtime(self.date).strftime('%d.%m.%Y'))

    def get_filename(self):
        if self.mimetype == 'application/vnd.ms-excel':  # HACK: we want .xls not .xlb for excel files
            ext = '.xls'
        else:
            ext = mimetypes.guess_extension(self.mimetype) or '.bin'
        name_slices = [
            self.doctype.name if self.doctype else 'Unterlage', self.name,
            self.version, timezone.localtime(self.date).strftime('%Y.%m.%d')
        ]
        if self.parent_object and hasattr(self.parent_object, 'get_filename_slice'):
            name_slices.insert(0, self.parent_object.get_filename_slice())
        name = slugify('-'.join(name_slices))
        return ''.join([name, ext])
    
    import os
    def store(self, file):
        from tempfile import NamedTemporaryFile
        # Save the file to a temporary location
        with NamedTemporaryFile(delete=False) as temp_file:
            for chunk in file.chunks():
                temp_file.write(chunk)

        try:
            # Call the encrypt_sign function with the temporary file path
            getVault()[self.uuid.hex] = temp_file.name
        finally:
            # Clean up: Delete the temporary file after encrypting/signing
            os.remove(temp_file.name)
    # def store(self, f):
    #     getVault()[self.uuid.hex] = f
    # from src.utils.gpgutils import encrypt_sign
    # def store(self, file_content):
    #     with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
    #         tmp_file.write(file_content.read())
    #         tmp_file_path = tmp_file.name

    #     try:
    #         getVault()[self.uuid.hex] = tmp_file_path
    #         encrypt_sign(tmp_file_path, encrypted_path, gpghome, encrypt_owner, signer_owner)
    #     finally:
    #         os.remove(tmp_file_path)

    def retrieve(self, user, context):
        hist = DownloadHistory.objects.create(document=self, user=user,
                                              context=context)

        f = getVault()[self.uuid.hex]
        if self.mimetype == 'application/pdf' and self.stamp_on_download:
            f = pdf_barcodestamp(f, hist.uuid.hex, str(user))
        return f

    def retrieve_raw(self):
        return getVault()[self.uuid.hex]
    class Meta:
        app_label = 'documents'


@receiver(post_delete, sender=Document)
def on_document_delete(sender, instance, **kwargs):
    try:
        del getVault()[instance.uuid.hex]
    except FileNotFoundError:
        # Ignore missing documents in debug mode, so documents can be deleted
        # when the storage vault is missing. Otherwise, this is a fatal error.
        if not settings.DEBUG:
            raise


class DownloadHistory(models.Model):
    document = models.ForeignKey(Document, on_delete=models.CASCADE, db_index=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    downloaded_at = models.DateTimeField(auto_now_add=True)
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, db_index=True)
    context = models.CharField(max_length=15)

    class Meta:
        app_label = 'documents'
        ordering = ['downloaded_at']
