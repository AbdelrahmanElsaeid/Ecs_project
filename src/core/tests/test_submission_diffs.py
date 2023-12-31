from django.utils.translation import gettext as _

from src.utils.testcases import EcsTestCase
from src.core.diff import diff_submission_forms
from src.core.tests.test_submissions import create_submission_form


class SubmissionFormDiffTest(EcsTestCase):
    '''Tests for the diff_submission_forms module
    
    Tests for changes between different submissionform versions.
    '''
    
    def setUp(self, *args, **kwargs):
        rval = super().setUp(*args, **kwargs)
        self.old_sf = create_submission_form()
        self.new_sf = create_submission_form()

        # both submission forms have to belong to the same submission
        self.new_sf.submission.current_submission_form = None
        self.new_sf.submission.save()
        self.new_sf.submission = self.old_sf.submission
        self.new_sf.save()

        return rval

    def test_submission_form_diff(self):
        '''Makes sure that if data field of a submissionform changes,
        this change ends up in the list of changes for that submissionform.
        Also checks that the value of the recorded change is correct.
        '''
        
        self.new_sf.project_title = 'roflcopter'
        diff = diff_submission_forms(self.old_sf, self.new_sf)
        self.assertTrue(diff['1.1 %s' % _('project title (english)')])
        self.assertEqual(diff['1.1 %s' % _('project title (english)')].new, 'roflcopter')
