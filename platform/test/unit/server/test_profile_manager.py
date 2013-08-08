#!/usr/bin/python
#
# Copyright (c) 2012 Red Hat, Inc.
#
#
# This software is licensed to you under the GNU General Public
# License as published by the Free Software Foundation; either version
# 2 of the License (GPLv2) or (at your option) any later version.
# There is NO WARRANTY for this software, express or implied,
# including the implied warranties of MERCHANTABILITY,
# NON-INFRINGEMENT, or FITNESS FOR A PARTICULAR PURPOSE. You should
# have received a copy of GPLv2 along with this software; if not, see
# http://www.gnu.org/licenses/old-licenses/gpl-2.0.txt.

import base
import mock
import pymongo

from pulp.plugins.profiler import Profiler
from pulp.server.db.model.consumer import Consumer, UnitProfile
from pulp.server.exceptions import MissingResource
from pulp.server.managers import factory


def get_profiler_by_type(content_type):
    """
    Return the superclass Profiler and an empty config.
    """
    return Profiler(), {}


@mock.patch('pulp.server.managers.consumer.profile.plugin_api.get_profiler_by_type',
            get_profiler_by_type)
class ProfileManagerTests(base.PulpAsyncServerTests):

    CONSUMER_ID = 'test-consumer'
    TYPE_1 = 'type-1'
    TYPE_2 = 'type-2'
    PROFILE_1 = {'name':'zsh', 'version':'1.0'}
    PROFILE_2 = {'name':'zsh', 'version':'2.0'}
    PROFILE_3 = {'name':'xxx', 'path':'/tmp/xxx'}

    def setUp(self):
        super(ProfileManagerTests, self).setUp()
        Consumer.get_collection().remove()
        UnitProfile.get_collection().remove()

    def tearDown(self):
        super(ProfileManagerTests, self).tearDown()
        Consumer.get_collection().remove()
        UnitProfile.get_collection().remove()

    def populate(self):
        manager = factory.consumer_manager()
        manager.register(self.CONSUMER_ID)

    def test_create(self):
        # Setup
        self.populate()
        # Test
        manager = factory.consumer_profile_manager()
        manager.create(self.CONSUMER_ID, self.TYPE_1, self.PROFILE_1)
        # Verify
        collection = UnitProfile.get_collection()
        cursor = collection.find({'consumer_id':self.CONSUMER_ID})
        profiles = list(cursor)
        self.assertEquals(len(profiles), 1)
        self.assertEquals(profiles[0]['consumer_id'], self.CONSUMER_ID)
        self.assertEquals(profiles[0]['content_type'], self.TYPE_1)
        self.assertEquals(profiles[0]['profile'], self.PROFILE_1)
        expected_hash = UnitProfile.calculate_hash(self.PROFILE_1)
        self.assertEqual(profiles[0]['profile_hash'], expected_hash)

    def test_get_profiles(self):
        # Setup
        self.populate()
        # Test
        manager = factory.consumer_profile_manager()
        manager.create(self.CONSUMER_ID, self.TYPE_1, self.PROFILE_1)
        manager.create(self.CONSUMER_ID, self.TYPE_2, self.PROFILE_2)
        profiles = manager.get_profiles(self.CONSUMER_ID)
        # Verify
        profiles = sorted(profiles)
        self.assertEquals(len(profiles), 2)
        self.assertEquals(profiles[0]['consumer_id'], self.CONSUMER_ID)
        self.assertEquals(profiles[0]['content_type'], self.TYPE_1)
        self.assertEquals(profiles[0]['profile'], self.PROFILE_1)
        expected_hash = UnitProfile.calculate_hash(self.PROFILE_1)
        self.assertEqual(profiles[0]['profile_hash'], expected_hash)
        self.assertEquals(profiles[1]['consumer_id'], self.CONSUMER_ID)
        self.assertEquals(profiles[1]['content_type'], self.TYPE_2)
        self.assertEquals(profiles[1]['profile'], self.PROFILE_2)
        expected_hash = UnitProfile.calculate_hash(self.PROFILE_2)
        self.assertEqual(profiles[1]['profile_hash'], expected_hash)

    def test_get_profiles_none(self):
        # Setup
        self.populate()
        # Test
        manager = factory.consumer_profile_manager()
        profiles = manager.get_profiles(self.CONSUMER_ID)
        self.assertEquals(len(profiles), 0)

    def test_get_profile(self):
        # Setup
        self.populate()
        # Test
        manager = factory.consumer_profile_manager()
        manager.create(self.CONSUMER_ID, self.TYPE_1, self.PROFILE_1)
        manager.create(self.CONSUMER_ID, self.TYPE_2, self.PROFILE_2)
        profile = manager.get_profile(self.CONSUMER_ID, self.TYPE_1)
        self.assertTrue(profile is not None)

    def test_get_profile_not_found(self):
        # Setup
        self.populate()
        # Test
        manager = factory.consumer_profile_manager()
        manager.create(self.CONSUMER_ID, self.TYPE_2, self.PROFILE_2)
        # Verify
        self.assertRaises(MissingResource, manager.get_profile, self.CONSUMER_ID, self.TYPE_1)

    def test_missing_consumer(self):
        # Test
        manager = factory.consumer_profile_manager()
        self.assertRaises(MissingResource, manager.update, self.CONSUMER_ID, self.TYPE_1, self.PROFILE_1)

    def test_update(self):
        # Setup
        self.populate()
        manager = factory.consumer_profile_manager()
        manager.update(self.CONSUMER_ID, self.TYPE_1, self.PROFILE_1)
        # Test
        manager.update(self.CONSUMER_ID, self.TYPE_1, self.PROFILE_2)
        # Verify
        collection = UnitProfile.get_collection()
        cursor = collection.find({'consumer_id':self.CONSUMER_ID})
        profiles = list(cursor)
        self.assertEquals(len(profiles), 1)
        self.assertEquals(profiles[0]['consumer_id'], self.CONSUMER_ID)
        self.assertEquals(profiles[0]['content_type'], self.TYPE_1)
        self.assertEquals(profiles[0]['profile'], self.PROFILE_2)
        expected_hash = UnitProfile.calculate_hash(self.PROFILE_2)
        self.assertEqual(profiles[0]['profile_hash'], expected_hash)

    def test_multiple_types(self):
        # Setup
        self.populate()
        collection = UnitProfile.get_collection()
        # Test
        manager = factory.consumer_profile_manager()
        manager.update(self.CONSUMER_ID, self.TYPE_1, self.PROFILE_1)
        manager.update(self.CONSUMER_ID, self.TYPE_2, self.PROFILE_2)
        # Verify
        cursor = collection.find({'consumer_id':self.CONSUMER_ID})
        cursor.sort('content_type', pymongo.ASCENDING)
        profiles = list(cursor)
        # Type_1
        self.assertEquals(len(profiles), 2)
        self.assertEquals(profiles[0]['consumer_id'], self.CONSUMER_ID)
        self.assertEquals(profiles[0]['content_type'], self.TYPE_1)
        self.assertEquals(profiles[0]['profile'], self.PROFILE_1)
        expected_hash = UnitProfile.calculate_hash(self.PROFILE_1)
        self.assertEqual(profiles[0]['profile_hash'], expected_hash)
        self.assertEquals(profiles[1]['consumer_id'], self.CONSUMER_ID)
        self.assertEquals(profiles[1]['content_type'], self.TYPE_2)
        self.assertEquals(profiles[1]['profile'], self.PROFILE_2)
        expected_hash = UnitProfile.calculate_hash(self.PROFILE_2)
        self.assertEqual(profiles[1]['profile_hash'], expected_hash)

    def test_fetch_by_type1(self):
        # Setup
        self.populate()
        collection = UnitProfile.get_collection()
        manager = factory.consumer_profile_manager()
        manager.update(self.CONSUMER_ID, self.TYPE_1, self.PROFILE_1)
        manager.update(self.CONSUMER_ID, self.TYPE_2, self.PROFILE_2)
        # Test
        profile = manager.get_profile(self.CONSUMER_ID, self.TYPE_1)
        # Verify
        self.assertTrue(profile is not None)
        self.assertEquals(profile['consumer_id'], self.CONSUMER_ID)
        self.assertEquals(profile['content_type'], self.TYPE_1)
        self.assertEquals(profile['profile'], self.PROFILE_1)
        expected_hash = UnitProfile.calculate_hash(self.PROFILE_1)
        self.assertEqual(profile['profile_hash'], expected_hash)

    def test_fetch_by_type2(self):
        # Setup
        self.populate()
        collection = UnitProfile.get_collection()
        manager = factory.consumer_profile_manager()
        manager.update(self.CONSUMER_ID, self.TYPE_1, self.PROFILE_1)
        manager.update(self.CONSUMER_ID, self.TYPE_2, self.PROFILE_2)
        # Test
        profile = manager.get_profile(self.CONSUMER_ID, self.TYPE_2)
        # Verify
        self.assertTrue(profile is not None)
        self.assertEquals(profile['consumer_id'], self.CONSUMER_ID)
        self.assertEquals(profile['content_type'], self.TYPE_2)
        self.assertEquals(profile['profile'], self.PROFILE_2)
        expected_hash = UnitProfile.calculate_hash(self.PROFILE_2)
        self.assertEqual(profile['profile_hash'], expected_hash)

    def test_delete(self):
        # Setup
        self.populate()
        collection = UnitProfile.get_collection()
        manager = factory.consumer_profile_manager()
        manager.update(self.CONSUMER_ID, self.TYPE_1, self.PROFILE_1)
        manager.update(self.CONSUMER_ID, self.TYPE_2, self.PROFILE_2)
        collection = UnitProfile.get_collection()
        cursor = collection.find({'consumer_id':self.CONSUMER_ID})
        profiles = list(cursor)
        self.assertEquals(len(profiles), 2)
        # Test
        manager.delete(self.CONSUMER_ID, self.TYPE_1)
        # Verify
        collection = UnitProfile.get_collection()
        cursor = collection.find({'consumer_id':self.CONSUMER_ID})
        profiles = list(cursor)
        self.assertEquals(len(profiles), 1)
        self.assertEquals(profiles[0]['consumer_id'], self.CONSUMER_ID)
        self.assertEquals(profiles[0]['content_type'], self.TYPE_2)
        self.assertEquals(profiles[0]['profile'], self.PROFILE_2)
        expected_hash = UnitProfile.calculate_hash(self.PROFILE_2)
        self.assertEqual(profiles[0]['profile_hash'], expected_hash)

    def test_consumer_deleted(self):
        # Setup
        self.populate()
        collection = UnitProfile.get_collection()
        manager = factory.consumer_profile_manager()
        manager.update(self.CONSUMER_ID, self.TYPE_1, self.PROFILE_1)
        manager.update(self.CONSUMER_ID, self.TYPE_2, self.PROFILE_2)
        collection = UnitProfile.get_collection()
        cursor = collection.find({'consumer_id':self.CONSUMER_ID})
        profiles = list(cursor)
        self.assertEquals(len(profiles), 2)
        # Test
        manager.consumer_deleted(self.CONSUMER_ID)
        cursor = collection.find()
        profiles = list(cursor)
        self.assertEquals(len(profiles), 0)

    def test_consumer_unregister_cleanup(self):
        # Setup
        self.test_create()
        # Test
        manager = factory.consumer_manager()
        manager.unregister(self.CONSUMER_ID)
        # Verify
        collection = UnitProfile.get_collection()
        cursor = collection.find({'consumer_id':self.CONSUMER_ID})
        profiles = list(cursor)
        self.assertEquals(len(profiles), 0)
