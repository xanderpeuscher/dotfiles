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

"""Unit tests for the kernel commands."""



import path_initializer
path_initializer.InitializeSysPath()

import copy

import gflags as flags
import unittest

from gcutil import command_base
from gcutil import kernel_cmds
from gcutil import mock_api

FLAGS = flags.FLAGS


class KernelCmdsTest(unittest.TestCase):

  def testGetKernelGeneratesCorrectRequest(self):
    flag_values = copy.deepcopy(FLAGS)

    command = kernel_cmds.GetKernel('getkernel', flag_values)

    expected_project = 'test_project'
    expected_kernel = 'test_kernel'
    flag_values.project = expected_project

    command.SetFlags(flag_values)
    command.SetApi(mock_api.MockApi())

    result = command.Handle(expected_kernel)

    self.assertEqual(result['project'], expected_project)
    self.assertEqual(result['kernel'], expected_kernel)

  def testNewestKernelsFilter(self):
    flag_values = copy.deepcopy(FLAGS)
    command = kernel_cmds.ListKernels('listkernels', flag_values)
    command.SetFlags(flag_values)

    def KernelSelfLink(name):
      return ('https://www.googleapis.com/compute/v1beta14/projects/'
              'google.com:myproject/global/kernels/%s') % name

    kernels = [
        {'selfLink': KernelSelfLink('versionlesskernel1')},
        {'selfLink': KernelSelfLink('kernel-v20130408')},
        {'selfLink': KernelSelfLink('kernel-v20130409')},
        {'selfLink': KernelSelfLink('kernel-v20130410')},
        {'selfLink': KernelSelfLink('kernel-x20130410')},
        {'selfLink': KernelSelfLink('kernel-x20130411')},
    ]

    flag_values.old_kernels = False
    validate = command_base.NewestKernelsFilter(flag_values, kernels)
    self.assertEqual(3, len(validate))
    self.assertEqual(
        KernelSelfLink('versionlesskernel1'), validate[0]['selfLink'])
    self.assertEqual(
        KernelSelfLink('kernel-v20130410'), validate[1]['selfLink'])
    self.assertEqual(
        KernelSelfLink('kernel-x20130411'), validate[2]['selfLink'])

    flag_values.old_kernels = True
    validate = command_base.NewestKernelsFilter(flag_values, kernels)
    self.assertEqual(6, len(validate))
    for i in range(len(kernels)):
      self.assertEqual(kernels[i]['selfLink'], validate[i]['selfLink'])

  def testPromptForKernels(self):
    flag_values = copy.deepcopy(FLAGS)
    flag_values.project = 'myproject'
    command = kernel_cmds.ListKernels('addkernel', flag_values)
    command.SetFlags(flag_values)

    class MockListApi(object):
      def __init__(self):
        self.projects = set()
        self.calls = 0

      # pylint: disable=redefined-builtin
      # pylint: disable=unused-argument
      def list(
          self, project=None, maxResults=None, filter=None, pageToken=None):
        self.projects.add(project)
        self.calls += 1
        return mock_api.MockRequest({'items': []})

    list_api = MockListApi()
    command._presenter.PromptForKernel(list_api)

    expected_projects = command_base.STANDARD_KERNEL_PROJECTS + ['myproject']
    self.assertEquals(len(expected_projects), list_api.calls)
    for project in expected_projects:
      self.assertTrue(project in list_api.projects)


if __name__ == '__main__':
  unittest.main()
