# -*- coding: utf-8 -*-

from flask import url_for

from rs_admin.tests.base import TestCase

class ViewsTestCase(TestCase):
    
    # nosetests -s -v rs_admin
    
        
    def test_urls(self):
        url = url_for("home")
        response = self.client.get(url)        
        self.assert200(response)
        self.assert_template_used('index.html')
        
        
