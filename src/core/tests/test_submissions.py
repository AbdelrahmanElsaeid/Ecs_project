import os

from django.utils import timezone

from src.core.models import Submission, SubmissionForm, EthicsCommission, Investigator
from src.documents.models import Document, DocumentType
from src.utils.testcases import EcsTestCase
from src.users.utils import get_or_create_user, create_user

TEST_PDF = os.path.join(os.path.dirname(__file__), 'data', 'menschenrechtserklaerung.pdf')

def attach_document(submission_form, filelike, name, doctype_identifier, mimetype='application/pdf', version="1", date=None):
    doctype = DocumentType.objects.get(identifier=doctype_identifier)
    date = date or timezone.now()
    doc = Document.objects.create(version=version, date=date, name=name,
        doctype=doctype, mimetype=mimetype, parent_object=submission_form)
    doc.store(filelike)
    submission_form.documents.add(doc)
    return doc

def create_submission_form(ec_number=None, presenter=None):
    presenter = presenter or get_or_create_user('test_presenter@example.com')[0]
    sub = Submission(ec_number=ec_number, presenter=presenter, susar_presenter=presenter)
    sub.save()
    sform = SubmissionForm.objects.create(
        submission = sub,
        project_title="High Risk Test Study",
        eudract_number="2010-002323-99",
        sponsor_name="testsponsor",
        sponsor_address="mainstreet 1",
        sponsor_zip_code="2323",
        sponsor_city="Wien",
        sponsor_phone="+4309876543456789",
        sponsor_fax="+430987654345678",
        sponsor_email="sponsor@example.com",
        invoice_name="",
        invoice_address="",
        invoice_zip_code="",
        invoice_city="",
        invoice_phone="",
        invoice_fax="",
        invoice_email="",
        invoice_uid="",
        project_type_non_reg_drug=True,
        project_type_reg_drug=False,
        project_type_reg_drug_within_indication=False,
        project_type_reg_drug_not_within_indication=False,
        project_type_medical_method=False,
        project_type_medical_device=False,
        project_type_medical_device_with_ce=False,
        project_type_medical_device_without_ce=False,
        project_type_medical_device_performance_evaluation=False,
        project_type_basic_research=False,
        project_type_genetic_study=False,
        project_type_register=False,
        project_type_biobank=False,
        project_type_retrospective=False,
        project_type_questionnaire=False,
        project_type_education_context=None,
        project_type_misc=None,
        specialism="Pädiatrische Onkologie / Immunologie",
        pharma_checked_substance="",
        pharma_reference_substance="",
        medtech_checked_product="",
        medtech_reference_substance="",
        clinical_phase="III",
        already_voted=True,
        subject_count=175,
        subject_minage=0,
        subject_maxage=21,
        subject_noncompetents=True,
        subject_males=True,
        subject_females=True,
        subject_childbearing=True,
        subject_duration="48 months",
        subject_duration_active="12 months",
        subject_duration_controls="36 months",
        subject_planned_total_duration="99",
        substance_preexisting_clinical_tries=True,
        substance_p_c_t_phase="III",
        substance_p_c_t_period="to long",
        substance_p_c_t_application_type="IV in children",
        substance_p_c_t_gcp_rules=True,
        substance_p_c_t_final_report=True,

        medtech_product_name="",
        medtech_manufacturer="",
        medtech_certified_for_exact_indications=False,
        medtech_certified_for_other_indications=False,
        medtech_ce_symbol=False,
        medtech_manual_included=False,
        medtech_technical_safety_regulations="",
        medtech_departure_from_regulations="",
        insurance_name="Insurance",
        insurance_address="insurancestreet 1",
        insurance_phone="+43123456",
        insurance_contract_number="",
        insurance_validity="",
        additional_therapy_info="long blabla",
        german_project_title="bla bla bla",
        german_summary="bla bla bla",
        german_preclinical_results="bla bla bla",
        german_primary_hypothesis="bla bla bla",
        german_inclusion_exclusion_crit="bla bla bla",
        german_ethical_info="bla bla bla",
        german_protected_subjects_info="bla bla bla",
        german_recruitment_info="bla bla bla",
        german_consent_info="bla bla bla",
        german_risks_info="bla bla bla",
        german_benefits_info="bla bla bla",
        german_relationship_info="bla bla bla",
        german_concurrent_study_info="bla bla bla",
        german_sideeffects_info="bla bla bla",
        german_statistical_info="bla bla bla",
        german_dataprotection_info="bla bla bla",
        german_aftercare_info="bla bla bla",
        german_payment_info="bla bla bla",
        german_abort_info="bla bla bla",
        german_dataaccess_info="bla bla bla",
        german_financing_info="bla bla bla",
        german_additional_info="bla bla bla",
        study_plan_blind=0,
        study_plan_observer_blinded=False,
        study_plan_randomized=True,
        study_plan_parallelgroups=True,
        study_plan_controlled=True,
        study_plan_cross_over=False,
        study_plan_placebo=False,
        study_plan_factorized=False,
        study_plan_pilot_project=False,
        study_plan_equivalence_testing=False,
        study_plan_misc=None,
        study_plan_number_of_groups="two sequential randomisations, each with 2 arms",
        study_plan_stratification="Age, Stage, National Groups",
        study_plan_sample_frequency=None,
        study_plan_primary_objectives="Event Free Survival",
        study_plan_null_hypothesis=False,
        study_plan_alternative_hypothesis="my thesis",
        study_plan_secondary_objectives="secondary objective",
        study_plan_alpha="0.03",
        study_plan_power="0.75",
        study_plan_statalgorithm="blabla",
        study_plan_multiple_test_correction_algorithm="",
        study_plan_dropout_ratio="0",
        study_plan_population_intention_to_treat=True,
        study_plan_population_per_protocol=False,
        study_plan_abort_crit="Peto",
        study_plan_planned_statalgorithm="log rank test",
        study_plan_dataquality_checking="None",
        study_plan_datamanagement="Datamanagement",
        study_plan_biometric_planning="Mag. rer.soc.oec. Jane Doe",
        study_plan_statistics_implementation="Mag. rer.soc.oec. Jane Doe / Statistikerin",
        #study_plan_dataprotection_anonalgoritm="Electronically generated unique patient number within SIOPEN-R-Net",
        study_plan_dataprotection_anonalgoritm="to long",
        study_plan_dataprotection_dvr="",
        study_plan_dataprotection_reason="",
        submitter_contact_gender="f",
        submitter_contact_first_name="Jane",
        submitter_contact_title="Univ. Doz. Dr.",
        submitter_contact_last_name="Doe",
        submitter_organisation="Organisation",
        submitter_jobtitle="jobtitle",
        submitter_is_coordinator=True,
        submitter_is_main_investigator=False,
        submitter_is_sponsor=False,
        submitter_is_authorized_by_sponsor=False,
        substance_registered_in_countries=[],
        substance_p_c_t_countries=['AT', 'DE', 'US'],
        presenter=presenter,
    )
    
    with open(TEST_PDF, 'rb') as f:
        attach_document(sform, f, 'protocol.pdf', 'protocol')
    
    ek1 = EthicsCommission(name='EK von Neverland')
    ek1.save()
    
    Investigator.objects.create(submission_form=sform, main=True, contact_last_name="Univ. Doz. Dr. Joseph doe", subject_count=1, ethics_commission=ek1)
    sform.render_pdf_document()
    return sform


class SubmissionFormTest(EcsTestCase):
    '''Tests for creating a submission form.
    
    Basic Tests for the modules Submission, SubmissionForm EthicsCommission, Investigator.
    '''
    
    def test_creation(self):
        '''Tests if a submission form can be created and saved.
        Also tests creation of an EthicsCommission and an Investigator and
        attaching the submissionform to the created EC and the Investigator.
        If a pdf of the submission form can be rendered is tested aswell.
        '''
        
        presenter=get_or_create_user('test_presenter@example.com')[0]
        sub = Submission(presenter=presenter, susar_presenter=presenter)
        sub.save()
        sform = SubmissionForm.objects.create(
            submission = sub,
            project_title="High Risk Test Study",
            eudract_number="2010-002323-99",
            sponsor_name="testsponsor",
            sponsor_address="mainstreet 1",
            sponsor_zip_code="2323",
            sponsor_city="Wien",
            sponsor_phone="+4309876543456789",
            sponsor_fax="+430987654345678",
            sponsor_email="sponsor@example.com",
            invoice_name="",
            invoice_address="",
            invoice_zip_code="",
            invoice_city="",
            invoice_phone="",
            invoice_fax="",
            invoice_email="",
            invoice_uid="",
            project_type_non_reg_drug=True,
            project_type_reg_drug=False,
            project_type_reg_drug_within_indication=False,
            project_type_reg_drug_not_within_indication=False,
            project_type_medical_method=False,
            project_type_medical_device=False,
            project_type_medical_device_with_ce=False,
            project_type_medical_device_without_ce=False,
            project_type_medical_device_performance_evaluation=False,
            project_type_basic_research=False,
            project_type_genetic_study=False,
            project_type_register=False,
            project_type_biobank=False,
            project_type_retrospective=False,
            project_type_questionnaire=False,
            project_type_education_context=None,
            project_type_misc=None,
            specialism="Pädiatrische Onkologie / Immunologie",
            pharma_checked_substance="",
            pharma_reference_substance="",
            medtech_checked_product="",
            medtech_reference_substance="",
            clinical_phase="III",
            already_voted=True,
            subject_count=175,
            subject_minage=0,
            subject_maxage=21,
            subject_noncompetents=True,
            subject_males=True,
            subject_females=True,
            subject_childbearing=True,
            subject_duration="48 months",
            subject_duration_active="12 months",
            subject_duration_controls="36 months",
            subject_planned_total_duration="99",
            substance_preexisting_clinical_tries=True,
            substance_p_c_t_phase="III",
            substance_p_c_t_period="to long",
            substance_p_c_t_application_type="IV in children",
            substance_p_c_t_gcp_rules=True,
            substance_p_c_t_final_report=True,

            medtech_product_name="",
            medtech_manufacturer="",
            medtech_certified_for_exact_indications=False,
            medtech_certified_for_other_indications=False,
            medtech_ce_symbol=False,
            medtech_manual_included=False,
            medtech_technical_safety_regulations="",
            medtech_departure_from_regulations="",
            insurance_name="Insurance",
            insurance_address="insurancestreet 1",
            insurance_phone="+43123456",
            insurance_contract_number="",
            insurance_validity="",
            additional_therapy_info="long blabla",
            german_project_title="bla bla bla",
            german_summary="bla bla bla",
            german_preclinical_results="bla bla bla",
            german_primary_hypothesis="bla bla bla",
            german_inclusion_exclusion_crit="bla bla bla",
            german_ethical_info="bla bla bla",
            german_protected_subjects_info="bla bla bla",
            german_recruitment_info="bla bla bla",
            german_consent_info="bla bla bla",
            german_risks_info="bla bla bla",
            german_benefits_info="bla bla bla",
            german_relationship_info="bla bla bla",
            german_concurrent_study_info="bla bla bla",
            german_sideeffects_info="bla bla bla",
            german_statistical_info="bla bla bla",
            german_dataprotection_info="bla bla bla",
            german_aftercare_info="bla bla bla",
            german_payment_info="bla bla bla",
            german_abort_info="bla bla bla",
            german_dataaccess_info="bla bla bla",
            german_financing_info="bla bla bla",
            german_additional_info="bla bla bla",
            study_plan_blind=0,
            study_plan_observer_blinded=False,
            study_plan_randomized=True,
            study_plan_parallelgroups=True,
            study_plan_controlled=True,
            study_plan_cross_over=False,
            study_plan_placebo=False,
            study_plan_factorized=False,
            study_plan_pilot_project=False,
            study_plan_equivalence_testing=False,
            study_plan_misc=None,
            study_plan_number_of_groups="two sequential randomisations, each with 2 arms",
            study_plan_stratification="Age, Stage, National Groups",
            study_plan_sample_frequency=None,
            study_plan_primary_objectives="Event Free Survival",
            study_plan_null_hypothesis=False,
            study_plan_alternative_hypothesis="my thesis",
            study_plan_secondary_objectives="secondary objective",
            study_plan_alpha="0.03",
            study_plan_power="0.75",
            study_plan_statalgorithm="blabla",
            study_plan_multiple_test_correction_algorithm="",
            study_plan_dropout_ratio="0",
            study_plan_population_intention_to_treat=True,
            study_plan_population_per_protocol=False,
            study_plan_abort_crit="Peto",
            study_plan_planned_statalgorithm="log rank test",
            study_plan_dataquality_checking="None",
            study_plan_datamanagement="Datamanagement",
            study_plan_biometric_planning="Mag. rer.soc.oec. Jane Doe",
            study_plan_statistics_implementation="Mag. rer.soc.oec. Jane Doe / Statistikerin",
            #study_plan_dataprotection_anonalgoritm="Electronically generated unique patient number within SIOPEN-R-Net",
            study_plan_dataprotection_anonalgoritm="to long",
            study_plan_dataprotection_dvr="",
            study_plan_dataprotection_reason="",
            submitter_contact_gender="f",
            submitter_contact_first_name="Jane",
            submitter_contact_title="Univ. Doz. Dr.",
            submitter_contact_last_name="Doe",
            submitter_organisation="Organisation",
            submitter_jobtitle="jobtitle",
            submitter_is_coordinator=True,
            submitter_is_main_investigator=False,
            submitter_is_sponsor=False,
            submitter_is_authorized_by_sponsor=False,
            substance_registered_in_countries=[],
            substance_p_c_t_countries=['AT', 'DE', 'US'],
            presenter=presenter,
        )
        # normal way would be to fetch one, but the test database does not contain the data rows :(
        ek1 = EthicsCommission(name='EK von Neverland')
        ek1.save()
        Investigator.objects.create(submission_form=sform, main=True, contact_last_name="Univ. Doz. Dr. Joseph doe", subject_count=1, ethics_commission=ek1)
        sform.render_pdf_document()


class SubmissionAttachUserTest(EcsTestCase):
    '''Tests for attaching users to a submission in different roles.
    
    '''
    
    def setUp(self):
        self.email = 'foobar@example.com'

        self.user = create_user(self.email)
        self.sender = create_user('root@example.com')
        self.sf = create_submission_form()

        self.sf.sponsor_email = self.email
        self.sf.investigator_email = self.email
        self.sf.submitter_email = self.email

        self.user.save()
        self.sender.save();
        self.sf.save()

    def test_submission_attach_user(self):
        '''Tests if a user can be attached to a study as submitter and as sponsor.'''

        for x in ('submitter', 'sponsor'):
            submission_forms = SubmissionForm.objects.filter(**{'{0}_email'.format(x): self.user.email})
            for sf in submission_forms:
                setattr(sf, x, self.user)
                sf.save()

        investigator_by_email = Investigator.objects.filter(email=self.user.email)
        for inv in investigator_by_email:
            inv.user = self.user
            inv.save()
        
        self.sf = SubmissionForm.objects.get(project_title="High Risk Test Study")
        self.assertEqual(self.sf.sponsor, self.user)
        self.assertEqual(self.sf.submitter, self.user)

    def tearDown(self):
        self.user.delete()
