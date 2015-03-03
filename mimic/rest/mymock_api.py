"""
@copyright: Copyright (c) 2014 Rackspace US, Inc.
"""
from collections import defaultdict
import json
from uuid import uuid4, UUID

from characteristic import attributes, Attribute
from six import text_type

from twisted.plugin import IPlugin
from twisted.web.http import NOT_FOUND, NOT_IMPLEMENTED
from twisted.web.server import Request
from zope.interface import implementer

from mimic.catalog import Entry
from mimic.catalog import Endpoint
from mimic.imimic import IAPIMock
from mimic.rest.mimicapp import MimicApp
from mimic.util.helper import random_ipv4, seconds_to_timestamp


@implementer(IAPIMock, IPlugin)
class MyAPIMock():

    def __init__(self, regions=("ORD",), default_pools=1):
        """
        Construct a :class:`RackConnectV3` object.
        """
        self.regions = regions
        self.default_pools = default_pools

    def catalog_entries(self,
                        tenant_id):
        return [
            Entry(tenant_id, "Test", "TestResource", [
                Endpoint(tenant_id, region, text_type(uuid4()), prefix="v3")
                for region in self.regions
            ])
        ]

    def resource_for_region(self, region, uri_prefix, session_store):
        """
        Return an IResource implementing a public RackConnect V3 region
        endpoint.
        """
        return TestRegion(
            iapi=self,
            uri_prefix=uri_prefix,
            session_store=session_store,
            region_name=region,
            default_pools=self.default_pools).app.resource()


@attributes(["iapi", "uri_prefix", "session_store", "region_name",
             "default_pools"])
class TestRegion(object):
    """
    A set of ``klein`` routes representing a RackConnect V3 endpoint.
    """
    app = MimicApp()

    @app.route("/v3/<string:tenant_id>/test_endpoint", branch=True)
    def get_test_endpoint(self, request, tenant_id):

        handler = TestResourceClass()
        return handler.app.resource()


class TestResourceClass(object):

    app = MimicApp()

    @app.route("/test", methods=["GET"])
    def list_all_load_balancer_pools(self, request):
        """
        API call to list all load balancer pools for the tenant and region
        correspoding to this handler.  Returns 200 always.

        http://docs.rcv3.apiary.io/#get-%2Fv3%2F%7Btenant_id%7D%2Fload_balancer_pools
        """
        return json.dumps({"hello":"test"})
    
