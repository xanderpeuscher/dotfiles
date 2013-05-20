# Copyright 2012 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Unit tests for address collection commands."""



import path_initializer
path_initializer.InitializeSysPath()

import copy

import gflags as flags
import unittest

from gcutil import address_cmds
from gcutil import mock_api

FLAGS = flags.FLAGS

ADDRESS_COLLECTION_SUPPORTED_VERSIONS = ('v1beta15',)


class AddressCmdsTest(unittest.TestCase):

  def _doReserveAddressGeneratesCorrectRequest(self, service_version):
    flag_values = copy.deepcopy(FLAGS)

    command = address_cmds.ReserveAddress('reserveaddress', flag_values)

    expected_project = 'test_project'
    expected_address = 'test_address'
    expected_description = 'test address'
    submitted_region = 'test-region'
    expected_source_address = '123.123.123.1'

    flag_values.service_version = service_version
    flag_values.project = expected_project
    flag_values.description = expected_description
    flag_values.region = submitted_region
    flag_values.source_address = expected_source_address

    command.SetFlags(flag_values)
    command.SetApi(mock_api.MockApi())

    result = command.Handle(expected_address)

    self.assertEqual(result['project'], expected_project)

    response_body = result['body']
    self.assertEqual(response_body['name'], expected_address)
    self.assertEqual(response_body['description'], expected_description)
    self.assertEqual(submitted_region, result['region'])
    self.assertEquals(response_body['address'], expected_source_address)

  def testReserveAddressGeneratesCorrectRequest(self):
    for version in ADDRESS_COLLECTION_SUPPORTED_VERSIONS:
      self._doReserveAddressGeneratesCorrectRequest(version)

  def _doTestGetAddressGeneratesCorrectRequest(self, service_version):
    flag_values = copy.deepcopy(FLAGS)

    command = address_cmds.GetAddress('getaddress', flag_values)

    expected_project = 'test_project'
    expected_address = 'test_address'
    flag_values.project = expected_project
    flag_values.service_version = service_version

    command.SetFlags(flag_values)
    command.SetApi(mock_api.MockApi())
    submitted_region = 'test-region'
    flag_values.region = submitted_region

    result = command.Handle(expected_address)

    self.assertEqual(result['project'], expected_project)
    self.assertEqual(result['address'], expected_address)
    self.assertEquals(submitted_region, result['region'])

  def testGetAddressGeneratesCorrectRequest(self):
    for version in ADDRESS_COLLECTION_SUPPORTED_VERSIONS:
      self._doTestGetAddressGeneratesCorrectRequest(version)

  def _doTestReleaseAddressGeneratesCorrectRequest(self, service_version):
    flag_values = copy.deepcopy(FLAGS)

    command = address_cmds.ReleaseAddress('releaseaddress', flag_values)

    expected_project = 'test_project'
    expected_address = 'test_address'
    flag_values.project = expected_project
    flag_values.service_version = service_version

    command.SetFlags(flag_values)
    command.SetApi(mock_api.MockApi())
    command._credential = mock_api.MockCredential()
    submitted_region = 'test-region'
    flag_values.region = submitted_region

    results, exceptions = command.Handle(expected_address)
    self.assertEqual(exceptions, [])
    self.assertEqual(len(results['items']), 1)
    result = results['items'][0]

    self.assertEqual(result['project'], expected_project)
    self.assertEqual(result['address'], expected_address)
    self.assertEqual(submitted_region, result['region'])

  def testReleaseAddressGeneratesCorrectRequest(self):
    for version in ADDRESS_COLLECTION_SUPPORTED_VERSIONS:
      self._doTestReleaseAddressGeneratesCorrectRequest(version)

  def _doTestReleaseAddressWithoutRegionFlag(self, service_version):
    flag_values = copy.deepcopy(FLAGS)

    command = address_cmds.ReleaseAddress('releaseaddress', flag_values)

    expected_project = 'test_project'
    expected_region = 'test-region'
    expected_address = 'test_address'
    address = ('projects/%s/regions/%s/addresses/%s' %
               (expected_project, expected_region, expected_address))
    flag_values.project = expected_project
    flag_values.service_version = service_version

    command.SetFlags(flag_values)
    command.SetApi(mock_api.MockApi())
    command._credential = mock_api.MockCredential()

    results, exceptions = command.Handle(address)
    self.assertEqual(exceptions, [])
    self.assertEqual(len(results['items']), 1)
    result = results['items'][0]

    self.assertEqual(result['project'], expected_project)
    self.assertEqual(result['address'], expected_address)
    self.assertEqual(expected_region, result['region'])

  def testReleaseAddressWithoutRegionFlag(self):
    for version in ADDRESS_COLLECTION_SUPPORTED_VERSIONS:
      self._doTestReleaseAddressGeneratesCorrectRequest(version)

  def _doTestReleaseMultipleAddresses(self, service_version):
    flag_values = copy.deepcopy(FLAGS)
    command = address_cmds.ReleaseAddress(
        'releaseaddress', flag_values)

    expected_project = 'test_project'
    expected_addresses = [
        'test-addresses-%02d' % x for x in xrange(100)]
    flag_values.service_version = service_version
    flag_values.project = expected_project
    flag_values.region = 'region-a'

    command.SetFlags(flag_values)
    command.SetApi(mock_api.MockApi())
    command._credential = mock_api.MockCredential()

    results, exceptions = command.Handle(*expected_addresses)
    self.assertEqual(exceptions, [])
    results = results['items']
    self.assertEqual(len(results), len(expected_addresses))

    for expected_address, result in zip(expected_addresses, results):
      self.assertEqual(result['project'], expected_project)
      self.assertEqual(result['address'], expected_address)

  def testReleaseMultipleAddresses(self):
    for version in ADDRESS_COLLECTION_SUPPORTED_VERSIONS:
      self._doTestReleaseMultipleAddresses(version)

if __name__ == '__main__':
  unittest.main()
