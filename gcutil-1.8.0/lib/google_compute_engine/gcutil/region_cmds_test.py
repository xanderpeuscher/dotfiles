#!/usr/bin/python
#
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

"""Unit tests for the region commands."""



import path_initializer
path_initializer.InitializeSysPath()

import copy

import gflags as flags
import unittest

from gcutil import command_base
from gcutil import mock_api
from gcutil import region_cmds

FLAGS = flags.FLAGS


class RegionCmdsTest(unittest.TestCase):

  def testGetRegionGeneratesCorrectRequest(self):
    flag_values = copy.deepcopy(FLAGS)

    command = region_cmds.GetRegion('getregion', flag_values)

    expected_jurisdiction = 'test_jurisdiction'
    expected_region = 'test_region'
    submitted_full_region = '%s-%s' % (expected_jurisdiction, expected_region)
    flag_values.service_version = command_base.CURRENT_VERSION

    command.SetFlags(flag_values)
    command.SetApi(mock_api.MockApi())

    result = command.Handle(submitted_full_region)

    self.assertEqual(result['region'], submitted_full_region)


if __name__ == '__main__':
  unittest.main()
