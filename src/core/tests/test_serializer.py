import os, datetime, uuid
from io import BytesIO

from src.utils.testcases import EcsTestCase
from src.core.serializer import Serializer
from src.core.models import Submission, SubmissionForm, Measure, EthicsCommission, Investigator, ForeignParticipatingCenter, NonTestedUsedDrug
from src.documents.models import Document, DocumentType
from src.users.utils import sudo, get_or_create_user

SUBMISSION_FORM_DATA = {
    'project_title': 'title',
    'subject_count': 10,
    'eudract_number': 'EUDRACT',
    'subject_minage': 18,
    'subject_maxage': 88,
    'project_type_misc': 'misc foo',
    'project_type_genetic_study': True,
    'submitter_contact_last_name': 'sn foo',
    'study_plan_blind': 0,
}

class SerializerTest(EcsTestCase):
    '''Tests for the serializer module
    
    Serializer module gets tested by exporting and import data and comparing the data afterwards.
    '''
    
    def create_submission_form(self):
        s = Submission.objects.create(ec_number=20109942)
        sf = SubmissionForm.objects.create(submission=s, **SUBMISSION_FORM_DATA)
        docs = []
        for i in range(3):
            doctype = DocumentType.objects.create(name='doctype-%s' % i)
            with open(os.path.join(os.path.dirname(__file__), 'data', 'menschenrechtserklaerung.pdf'), 'rb') as f:
                doc = Document.objects.create(doctype=doctype,
                    version='v%s' % i, date=datetime.date(2010, 0o3, 10))
                doc.store(f)
                docs.append(doc)
        sf.documents = docs
        for cat in ('6.1', '6.2'):
            for i in range(2):
                Measure.objects.create(submission_form=sf, category=cat, type="t-%s" % i, period="p-%s" % i, total="t-%s" % i)
        for i in range(3):
            ForeignParticipatingCenter.objects.create(submission_form=sf, name="fpc-%s" % i)
        for i in range(3):
            NonTestedUsedDrug.objects.create(submission_form=sf, generic_name="gn-%s" % i, preparation_form="pf-%s" % i, dosage="d-%s" % i)
        for i in range(2):
            ec = EthicsCommission.objects.create(name="ethics-commission-%s" % i, uuid=uuid.uuid4().hex)
            investigator = Investigator.objects.create(submission_form=sf, main=bool(i), ethics_commission=ec, contact_last_name="investigator-%s" % i, subject_count=3+i)
            for j in range(2):
                investigator.employees.create(sex='m', surname='s-%s-%s' % (i, j), firstname='s-%s-%s' % (i, j))
        sf.render_pdf_document()
        return sf
        
    def compare(self, a, b):
        self.assertEqual(type(a), type(b))
        for attr, value in SUBMISSION_FORM_DATA.items():
            self.assertEqual(getattr(a, attr), value)
            self.assertEqual(getattr(b, attr), value)
            
        get_doc_set = lambda x: set((doc.doctype, doc.version, doc.date, doc.mimetype) for doc in x.documents.all())
        self.assertEqual(get_doc_set(a), get_doc_set(b))
        
        get_measure_set = lambda x: set((m.category, m.type, m.period, m.total) for m in x.measures.all())
        self.assertEqual(get_measure_set(a), get_measure_set(b))
        
        get_employee_set = lambda x: frozenset((e.sex, e.firstname, e.surname) for e in x.employees.all())
        get_investigator_set = lambda x: set((i.contact_last_name, i.main, i.ethics_commission, i.subject_count, get_employee_set(i)) for i in x.investigators.all())
        self.assertEqual(get_investigator_set(a), get_investigator_set(b))
        
        get_fpc_set = lambda x: set((fpc.name,) for fpc in x.foreignparticipatingcenter_set.all())
        self.assertEqual(get_fpc_set(a), get_fpc_set(b))
        
        get_ntud_set = lambda x: set((ntud.generic_name, ntud.preparation_form, ntud.dosage) for ntud in x.nontesteduseddrug_set.all())
        self.assertEqual(get_ntud_set(a), get_ntud_set(b))
    
    def test_import_export(self):
        '''Tests the serializer by comparing original submission data
        against imported submission data that was previously exported
        from the original submission data.
        '''
        
        with sudo(get_or_create_user('test_presenter@example.com')[0]):
            sf = self.create_submission_form()
            buf = BytesIO()
            serializer = Serializer()
            serializer.write(sf, buf)
            cp = serializer.read(buf)
            self.compare(sf, cp)

