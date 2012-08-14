from DateTime import DateTime
from Products.CMFCore.utils import getToolByName
from Products.validation import validation
from Products.validation import validation as validationService
from Testing.makerequest import makerequest
from bika.lims.testing import BIKA_LIMS_INTEGRATION_TESTING
from bika.lims.testing import BIKA_LIMS_FIXTURE
from bika.lims.tests.base import BikaIntegrationTestCase
from plone.app.testing import *
from plone.testing import z2
import unittest,random
import transaction

class Tests(BikaIntegrationTestCase):

    defaultBases = (BIKA_LIMS_FIXTURE,)

    def test_AR(self):
        login(self.portal, TEST_USER_NAME)

        profiles = ['Digestible Energy', 'Micro-Bio check', 'Micro-Bio counts']
        sampletypes = [p.getObject() for p in self.bsc(portal_type="SampleType")]
        samplepoints = [p.getObject() for p in self.bsc(portal_type="SamplePoint")]

        client = self.portal.clients['client-1'] # happy hills
        contacts = [c for c in client.objectValues() if c.portal_type == 'Contact']
        for profile in profiles:
            profile = self.bsc(portal_type='AnalysisProfile',
                               Title=profile)[0].getObject()
            profile_services = profile.getService()

            _ars = []
            sample_id = client.invokeFactory(type_name = 'Sample', id = 'tmp')
            sample = client[sample_id]
            sample.edit(
                SampleID = sample_id,
                SampleType = random.choice(sampletypes).Title(),
                SamplePoint = random.choice(samplepoints).Title(),
                ClientReference = chr(random.randint(70,90))*5,
                ClientSampleID = chr(random.randint(70,90))*5,
                SamplingDate = DateTime()
            )
            sample.processForm()
            self.assertEqual(len(sample.getId().split("-")), 2)
            ar_id = client.invokeFactory("AnalysisRequest", id = 'tmp')
            ar = client[ar_id]
            _ars.append(ar)
            ar.edit(
                RequestID = ar_id,
                Contact = contacts[0],
                CCContact = contacts[1],
                CCEmails = "",
                Sample = sample,
                Profile = profile,
                ClientOrderNumber = chr(random.randint(70,90))*10
            )
            ar.processForm()
            self.assertEqual(len(ar.getId().split("-")), 3)
            prices = {}
            service_uids = []
            for service in profile_services:
                service_uids.append(service.UID())
                prices[service.UID()] = service.getPrice()
            ar.setAnalyses(service_uids, prices = prices)
        #for ar in _ars:
        #    self.workflow.doActionFor(ar, 'receive')
        #    self.assertEqual(portal_workflow.getInfoFor(ar, 'review_state', ''),
        #                     'sample_received')

        transaction.get().commit()

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(Tests))
    suite.layer = BIKA_LIMS_INTEGRATION_TESTING
    return suite
