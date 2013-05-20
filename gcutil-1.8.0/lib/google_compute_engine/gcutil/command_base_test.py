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

"""Unit tests for the base command classes."""

from __future__ import with_statement



import path_initializer
path_initializer.InitializeSysPath()

import copy
import datetime
import os
import sys
import tempfile


import oauth2client.client as oauth2_client


from google.apputils import app
import gflags as flags
import unittest

from gcutil import command_base
from gcutil import gcutil_logging
from gcutil import mock_api

FLAGS = flags.FLAGS


class CommandBaseTest(unittest.TestCase):

  class ListMockCommandBase(command_base.GoogleComputeListCommand):
    """A list mock command that specifies no default sort field."""

    print_spec = command_base.ResourcePrintSpec(
        summary=(
            ('name', 'id'),
            ('id', 'number'),
            ('description', 'description')),
        detail=(
            ('name', 'id'),
            ('id', 'number'),
            ('description', 'description')),
        sort_by=None)

    def __init__(self, name, flag_values):
      super(CommandBaseTest.ListMockCommandBase, self).__init__(
          name, flag_values)

    def SetApi(self, api):
      pass

    def ListFunc(self):

      # pylint: disable=unused-argument
      def Func(project=None, maxResults=None, filter=None, pageToken=None):
        return mock_api.MockRequest(
            {'items': [{'description': 'Object C',
                        'id': 'projects/user/objects/my-object-c',
                        'kind': 'cloud#object',
                        'number': 123},
                       {'description': 'Object A',
                        'id': 'projects/user/objects/my-object-a',
                        'kind': 'cloud#object',
                        'number': 789},
                       {'description': 'Object B',
                        'id': 'projects/user/objects/my-object-b',
                        'kind': 'cloud#object',
                        'number': 456},
                       {'description': 'Object D',
                        'id': 'projects/user/objects/my-object-d',
                        'kind': 'cloud#object',
                        'number': 999}],
             'kind': 'cloud#objectList'})

      return Func

  class ListMockCommand(ListMockCommandBase):
    """A list mock command that specifies a default sort field."""
    print_spec = command_base.ResourcePrintSpec(
        summary=(
            ('name', 'id'),
            ('id', 'number'),
            ('description', 'description')),
        detail=(
            ('name', 'id'),
            ('id', 'number'),
            ('description', 'description')),
        sort_by='name')

    def __init__(self, name, flag_values):
      super(CommandBaseTest.ListMockCommand, self).__init__(name, flag_values)

  class MockDetailCommand(command_base.GoogleComputeCommand):

    print_spec = command_base.ResourcePrintSpec(
        summary=(
            ('name', 'id'),
            ('id', 'number'),
            ('description', 'description'),
            ('additional', 'moreStuff')),
        detail=(
            ('name', 'id'),
            ('id', 'number'),
            ('description', 'description'),
            ('additional', 'moreStuff')),
        sort_by='name')

    def __init__(self, name, flag_values):
      super(CommandBaseTest.MockDetailCommand, self).__init__(name, flag_values)

    def SetApi(self, api):
      pass

    def Handle(self):
      return {'description': 'Object C',
              'id': 'projects/user/objects/my-object-c',
              'kind': 'cloud#object',
              'number': 123,
              'moreStuff': 'foo'}

  class MockSafetyCommand(command_base.GoogleComputeCommand):

    safety_prompt = 'Take scary action'

    def __init__(self, name, flag_values):
      super(CommandBaseTest.MockSafetyCommand, self).__init__(name, flag_values)

    def SetApi(self, api):
      pass

    def Handle(self):
      pass

  class MockSafetyCommandWithArgs(MockSafetyCommand):
    safety_prompt = 'Act on'

    def Handle(self, argument, arg2):
      pass

  class FakeExit(object):
    """A fake version of exit to capture exit status."""

    def __init__(self):
      self.__status__ = []

    def __call__(self, value):
      self.__status__.append(value)

    def GetStatuses(self):
      return self.__status__

  class CaptureOutput(object):

    def __init__(self):
      self._capture_text = ''

    # Purposefully name this 'write' to mock an output stream
    # pylint: disable-msg=C6409
    def write(self, text):
      self._capture_text += text

    # Purposefully name this 'flush' to mock an output stream
    # pylint: disable-msg=C6409
    def flush(self):
      pass

    def GetCapturedText(self):
      return self._capture_text

  class MockInput(object):

    def __init__(self, input_string):
      self._input_string = input_string

    # Purposefully name this 'readline' to mock an input stream
    # pylint: disable-msg=C6409
    def readline(self):
      return self._input_string

  def ClearLogger(self):
    for h in gcutil_logging.LOGGER.handlers:
      gcutil_logging.LOGGER.removeHandler(h)

  def testAuthRetries(self):

    class MockAuthCommand(command_base.GoogleComputeCommand):
      def __init__(self, name, flag_values):
        super(MockAuthCommand, self).__init__(name, flag_values)
        self.refresh_errors_to_throw = 0
        self.run_calls = 0

      def Reset(self):
        self.refresh_errors_to_throw = 0
        self.run_calls = 0

      def SetApi(self, api):
        pass

      def RunWithFlagsAndPositionalArgs(self, unused_flags, unused_args):
        self.run_calls += 1
        if self.refresh_errors_to_throw:
          self.refresh_errors_to_throw -= 1
          raise oauth2_client.AccessTokenRefreshError()
        return 'success', []

    project_flag = FLAGS.project
    try:
      FLAGS.project = 'someproject'
      command = MockAuthCommand('auth', copy.deepcopy(FLAGS))

      self.assertEqual(0, command.Run([]))
      self.assertEqual(1, command.run_calls)
      command.Reset()

      command.refresh_errors_to_throw = 1
      self.assertEqual(0, command.Run([]))
      self.assertEqual(2, command.run_calls)
      command.Reset()

      command.refresh_errors_to_throw = 2
      self.assertEqual(1, command.Run([]))
      self.assertEqual(2, command.run_calls)
      command.Reset()
    finally:
      FLAGS.project = project_flag

  def testPresentElement(self):
    class MockCommand(command_base.GoogleComputeCommand):
      def __init__(self, name, flag_values):
        super(MockCommand, self).__init__(name, flag_values)

    flag_values = copy.deepcopy(FLAGS)
    command = MockCommand('mock_command', flag_values)
    flag_values.project = 'user'
    flag_values.service_version = 'v1beta15'
    command.SetFlags(flag_values)

    self.assertEqual(
        'user',
        command._presenter.PresentElement(
            'https://www.googleapis.com/compute/v1/projects/user'))
    self.assertEqual(
        'user',
        command._presenter.PresentElement(
            'https://www.googleapis.com/compute/v1/projects/user/'))
    self.assertEqual('user', command._presenter.PresentElement('projects/user'))
    self.assertEqual(
        'user', command._presenter.PresentElement('projects/user/'))
    self.assertEqual(
        'standard-2-cpu',
        command._presenter.PresentElement(
            'https://www.googleapis.com/compute/v1/'
            'projects/user/machineTypes/standard-2-cpu'))
    self.assertEqual(
        'standard-2-cpu',
        command._presenter.PresentElement(
            'https://www.googleapis.com/compute/v1/'
            'projects/user/machineTypes/standard-2-cpu/'))
    self.assertEqual(
        'standard-2-cpu',
        command._presenter.PresentElement(
            'projects/user/machineTypes/standard-2-cpu'))
    self.assertEqual(
        'standard-2-cpu',
        command._presenter.PresentElement(
            'projects/user/machineTypes/standard-2-cpu/'))
    self.assertEqual(
        'foo/bar/baz',
        command._presenter.PresentElement(
            'https://www.googleapis.com/compute/v1/'
            'projects/user/shared-fate-zones/foo/bar/baz'))
    self.assertEqual(
        'foo/bar/baz',
        command._presenter.PresentElement(
            'projects/user/shared-fate-zones/foo/bar/baz'))
    self.assertEqual(
        'foo/bar/baz', command._presenter.PresentElement('foo/bar/baz'))

    # Tests eliding feature
    test_str = ('I am the very model of a modern Major-General. I\'ve '
                'information vegetable, animal, and mineral. I know the kings '
                'of England and quote the fights historical; from Marathon to '
                'Waterloo in order categorical.')
    self.assertEqual(
        'I am the very model of a modern.. Waterloo in order categorical.',
        command._presenter.PresentElement(test_str))

    flag_values.long_values_display_format = 'full'
    command.SetFlags(flag_values)
    self.assertEqual(test_str, command._presenter.PresentElement(test_str))

  def testDenormalizeProjectName(self):
    denormalize = command_base.GoogleComputeCommand.DenormalizeProjectName
    flag_values = flags.FlagValues()
    flags.DEFINE_string('project',
                        None,
                        'Project Name',
                        flag_values=flag_values)
    flags.DEFINE_string('project_id',
                        None,
                        'Obsolete Project Name',
                        flag_values=flag_values)

    self.assertRaises(command_base.CommandError,
                      denormalize,
                      flag_values)

    flag_values.project = 'project_collection/google'
    self.assertRaises(command_base.CommandError,
                      denormalize,
                      flag_values)

    flag_values.project = 'projects/google'
    denormalize(flag_values)
    self.assertEqual(flag_values.project, 'google')
    denormalize(flag_values)
    self.assertEqual(flag_values.project, 'google')

    flag_values.project = '/google'
    denormalize(flag_values)
    self.assertEqual(flag_values.project, 'google')

    flag_values.project = 'google/'
    denormalize(flag_values)
    self.assertEqual(flag_values.project, 'google')

    flag_values.project = '/google/'
    denormalize(flag_values)
    self.assertEqual(flag_values.project, 'google')

    flag_values.project = '/projects/google'
    denormalize(flag_values)
    self.assertEqual(flag_values.project, 'google')

    flag_values.project = 'projects/google/'
    denormalize(flag_values)
    self.assertEqual(flag_values.project, 'google')

    flag_values.project = '/projects/google/'
    denormalize(flag_values)
    self.assertEqual(flag_values.project, 'google')

    flag_values.project_id = 'my-obsolete-project-1'
    flag_values.project = 'my-new-project-1'
    denormalize(flag_values)
    self.assertEqual(flag_values.project, 'my-new-project-1')
    self.assertEqual(flag_values.project_id, None)

    flag_values.project_id = 'my-new-project-2'
    flag_values.project = None
    denormalize(flag_values)
    self.assertEqual(flag_values.project, 'my-new-project-2')
    self.assertEqual(flag_values.project_id, None)

    flag_values.project_id = 'MyUppercaseProject-1'
    flag_values.project = None
    self.assertRaises(command_base.CommandError, denormalize, flag_values)

    flag_values.project = 'MyUppercaseProject-2'
    flag_values.project_id = None
    self.assertRaises(command_base.CommandError, denormalize, flag_values)

  def testDenormalizeResourceName(self):
    denormalize = command_base.GoogleComputeCommand.DenormalizeResourceName
    self.assertEqual('dual-cpu',
                     denormalize('projects/google/machineTypes/dual-cpu'))
    self.assertEqual('dual-cpu',
                     denormalize('/projects/google/machineTypes/dual-cpu'))
    self.assertEqual('dual-cpu',
                     denormalize('projects/google/machineTypes/dual-cpu/'))
    self.assertEqual('dual-cpu',
                     denormalize('/projects/google/machineTypes/dual-cpu/'))
    self.assertEqual('dual-cpu',
                     denormalize('//projects/google/machineTypes/dual-cpu//'))
    self.assertEqual('dual-cpu',
                     denormalize('dual-cpu'))
    self.assertEqual('dual-cpu',
                     denormalize('/dual-cpu'))
    self.assertEqual('dual-cpu',
                     denormalize('dual-cpu/'))
    self.assertEqual('dual-cpu',
                     denormalize('/dual-cpu/'))

  def _DoTestNormalizeResourceName(self, service_version):
    class MockCommand(command_base.GoogleComputeCommand):
      def __init__(self, name, flag_values):
        super(MockCommand, self).__init__(name, flag_values)

    flag_values = copy.deepcopy(FLAGS)
    flag_values.project = 'google'
    flag_values.service_version = service_version

    command = MockCommand('mock_command', flag_values)
    command.SetFlags(flag_values)

    prefix = 'https://www.googleapis.com/compute/%s' % service_version
    expected = '%s/projects/google/machineTypes/dual-cpu' % prefix

    self.assertEqual(
        expected,
        command.NormalizeResourceName('google', None, 'machineTypes',
                                      'dual-cpu'))
    self.assertEqual(
        expected,
        command.NormalizeResourceName('google', None, 'machineTypes',
                                      '/dual-cpu'))
    self.assertEqual(
        expected,
        command.NormalizeResourceName('google', None, 'machineTypes',
                                      'dual-cpu/'))
    self.assertEqual(
        expected,
        command.NormalizeResourceName('google', None, 'machineTypes',
                                      '/dual-cpu/'))
    self.assertEqual(
        expected,
        command.NormalizeResourceName(
            'google',
            None,
            'machineTypes',
            'projects/google/machineTypes/dual-cpu'))
    self.assertEqual(
        expected,
        command.NormalizeResourceName(
            'google',
            None,
            'machineTypes',
            '/projects/google/machineTypes/dual-cpu'))
    self.assertEqual(
        expected,
        command.NormalizeResourceName(
            'google',
            None,
            'machineTypes',
            'projects/google/machineTypes/dual-cpu/'))
    self.assertEqual(
        expected,
        command.NormalizeResourceName(
            'google',
            None,
            'machineTypes',
            '/projects/google/machineTypes/dual-cpu/'))
    self.assertEqual(
        '%s/projects/google/kernels/default' % prefix,
        command.NormalizeResourceName(
            'my-project',
            None,
            'kernels',
            'projects/google/kernels/default'))

  def testNormalizeResourceName(self):
    for version in command_base.SUPPORTED_VERSIONS:
      self._DoTestNormalizeResourceName(version)

  def testNormalizeScopedResourceName(self):
    class MockCommand(command_base.GoogleComputeCommand):
      def __init__(self, name, flag_values):
        super(MockCommand, self).__init__(name, flag_values)

    flag_values = copy.deepcopy(FLAGS)
    flag_values.project = 'my-project'

    command = MockCommand('mock_command', flag_values)
    command.SetFlags(flag_values)

    # Validate scope is ignored downlevel
    flag_values.service_version = 'v1beta15'
    prefix = 'https://www.googleapis.com/compute/v1beta15'
    expected = '%s/projects/my-project/scope/objects/foo-bar' % prefix
    self.assertEqual(
        expected,
        command.NormalizeResourceName('my-project', 'scope', 'objects',
                                      'foo-bar'))

    # Validate scope is expected in v1beta14 and above
    flag_values.service_version = 'v1beta14'
    prefix = 'https://www.googleapis.com/compute/v1beta14'

    expected = '%s/projects/my-project/scope/objects/foo-bar' % prefix
    self.assertEqual(
        expected,
        command.NormalizeResourceName('my-project', 'scope', 'objects',
                                      'foo-bar'))

    # Validate helper wrappers
    expected = '%s/projects/my-project/objects/foo-bar' % prefix
    self.assertEqual(
        expected,
        command.NormalizeTopLevelResourceName('my-project', 'objects',
                                              'foo-bar'))

    expected = '%s/projects/my-project/global/objects/foo-bar' % prefix
    self.assertEqual(
        expected,
        command.NormalizeGlobalResourceName('my-project', 'objects',
                                            'foo-bar'))

    expected = '%s/projects/my-project/zones/zone-a/objects/foo-bar' % prefix
    self.assertEqual(
        expected,
        command.NormalizePerZoneResourceName('my-project', 'zone-a', 'objects',
                                             'foo-bar'))

  def testFlattenToDict(self):
    class TestClass(command_base.GoogleComputeCommand):
      fields = (('name', 'id'),
                ('simple', 'path.to.object'),
                ('multiple', 'more.elements'),
                ('multiple', 'even_more.elements'),
                ('repeated', 'things'),
                ('long', 'l'),
                ('does not exist', 'dne'),
                ('partial match', 'path.to.nowhere'),
               )

    data = {'id': ('https://www.googleapis.com/compute/v1beta1/' +
                   'projects/test/object/foo'),
            'path': {'to': {'object': 'bar'}},
            'more': [{'elements': 'a'}, {'elements': 'b'}],
            'even_more': [{'elements': 800}, {'elements': 800}],
            'things': [1, 2, 3],
            'l': 'n' * 80}
    expected_result = ['foo', 'bar', 'a,b', '800,800', '1,2,3',
                       '%s..%s' % ('n' * 31, 'n' * 31), '', '']
    flag_values = copy.deepcopy(FLAGS)
    flag_values.project = 'test'
    test_class = TestClass('foo', flag_values)
    test_class.SetFlags(flag_values)
    flattened = test_class._FlattenObjectToList(data, test_class.fields)
    self.assertEquals(flattened, expected_result)

  def testFlattenToDictWithMultipleTargets(self):
    class TestClass(command_base.GoogleComputeCommand):
      fields = (('name', ('name', 'id')),
                ('simple', ('path.to.object', 'foo')),
                ('multiple', 'more.elements'),
                ('multiple', 'even_more.elements'),
                ('repeated', 'things'),
                ('long', ('l', 'longer')),
                ('does not exist', 'dne'),
                ('partial match', 'path.to.nowhere'),
               )

    data = {'name': ('https://www.googleapis.com/compute/v1beta1/' +
                     'projects/test/object/foo'),
            'path': {'to': {'object': 'bar'}},
            'more': [{'elements': 'a'}, {'elements': 'b'}],
            'even_more': [{'elements': 800}, {'elements': 800}],
            'things': [1, 2, 3],
            'longer': 'n' * 80}
    expected_result = ['foo', 'bar', 'a,b', '800,800', '1,2,3',
                       '%s..%s' % ('n' * 31, 'n' * 31), '', '']
    flag_values = copy.deepcopy(FLAGS)
    flag_values.project = 'test'
    test_class = TestClass('foo', flag_values)
    test_class.SetFlags(flag_values)
    flattened = test_class._FlattenObjectToList(data, test_class.fields)
    self.assertEquals(flattened, expected_result)

  def testPositionArgumentParsing(self):
    class MockCommand(command_base.GoogleComputeCommand):

      def __init__(self, name, flag_values):
        super(MockCommand, self).__init__(name, flag_values)
        flags.DEFINE_string('mockflag',
                            'wrong_mock_flag',
                            'Mock Flag',
                            flag_values=flag_values)

      def Handle(self, arg1, arg2, arg3):
        pass

    flag_values = copy.deepcopy(FLAGS)
    command = MockCommand('mock_command', flag_values)

    expected_arg1 = 'foo'
    expected_arg2 = 'bar'
    expected_arg3 = 'baz'
    expected_flagvalue = 'wow'

    command_line = ['mock_command', expected_arg1, expected_arg2,
                    expected_arg3, '--mockflag=' + expected_flagvalue]

    # Verify the positional argument parser correctly identifies the parameters
    # and flags.
    result = command._ParseArgumentsAndFlags(flag_values, command_line)

    self.assertEqual(result[0], expected_arg1)
    self.assertEqual(result[1], expected_arg2)
    self.assertEqual(result[2], expected_arg3)
    self.assertEqual(flag_values.mockflag, expected_flagvalue)

  def testErroneousKeyWordArgumentParsing(self):
    class MockCommand(command_base.GoogleComputeCommand):

      def __init__(self, name, flag_values):
        super(MockCommand, self).__init__(name, flag_values)
        flags.DEFINE_integer('mockflag',
                             10,
                             'Mock Flag',
                             flag_values=flag_values,
                             lower_bound=0)

      def Handle(self, arg1, arg2, arg3):
        pass

    flag_values = copy.deepcopy(FLAGS)
    command = MockCommand('mock_command', flag_values)

    # Ensures that a type mistmatch for a keyword argument causes a
    # CommandError to be raised.
    bad_values = [-100, -2, 0.2, .30, 100.1]
    for val in bad_values:
      command_line = ['mock_command', '--mockflag=%s' % val]
      self.assertRaises(command_base.CommandError,
                        command._ParseArgumentsAndFlags,
                        flag_values, command_line)

    # Ensures that passing a nonexistent keyword argument also causes
    # a CommandError to be raised.
    command_line = ['mock_command', '--nonexistent_flag=boo!']
    self.assertRaises(command_base.CommandError,
                      command._ParseArgumentsAndFlags,
                      flag_values, command_line)

  def testSafetyPromptYes(self):
    flag_values = copy.deepcopy(FLAGS)
    command_line = ['mock_command']

    command = CommandBaseTest.MockSafetyCommand('mock_command', flag_values)
    args = command._ParseArgumentsAndFlags(flag_values, command_line)
    command.SetFlags(flag_values)

    mock_output = mock_api.MockOutput()
    mock_input = mock_api.MockInput('Y\n\r')

    oldin = sys.stdin
    sys.stdin = mock_input
    oldout = sys.stdout
    sys.stdout = mock_output

    result = command._HandleSafetyPrompt(args)

    self.assertEqual(mock_output.GetCapturedText(),
                     'Take scary action? [y/N]\n>>> ')
    self.assertEqual(result, True)

    sys.stdin = oldin
    sys.stdout = oldout

  def testSafetyPromptWithArgsYes(self):
    flag_values = copy.deepcopy(FLAGS)
    command_line = ['mock_cmd', 'arg1', 'arg2']

    command = CommandBaseTest.MockSafetyCommandWithArgs('mock_cmd', flag_values)
    args = command._ParseArgumentsAndFlags(flag_values, command_line)
    command.SetFlags(flag_values)

    mock_output = CommandBaseTest.CaptureOutput()
    mock_input = CommandBaseTest.MockInput('Y\n\r')

    oldin = sys.stdin
    sys.stdin = mock_input
    oldout = sys.stdout
    sys.stdout = mock_output

    result = command._HandleSafetyPrompt(args)

    self.assertEqual(mock_output.GetCapturedText(),
                     'Act on arg1, arg2? [y/N]\n>>> ')
    self.assertEqual(result, True)

    sys.stdin = oldin
    sys.stdout = oldout

  def testSafetyPromptMissingArgs(self):
    flag_values = copy.deepcopy(FLAGS)
    command_line = ['mock_cmd', 'arg1']

    command = CommandBaseTest.MockSafetyCommandWithArgs('mock_cmd', flag_values)

    command_base.sys.exit = CommandBaseTest.FakeExit()
    sys.stderr = CommandBaseTest.CaptureOutput()

    gcutil_logging.SetupLogging()
    self.assertRaises(command_base.CommandError,
                      command._ParseArgumentsAndFlags,
                      flag_values, command_line)

  def testSafetyPromptExtraArgs(self):
    flag_values = copy.deepcopy(FLAGS)
    command_line = ['mock_cmd', 'arg1', 'arg2', 'arg3']

    command = CommandBaseTest.MockSafetyCommandWithArgs('mock_cmd', flag_values)

    command_base.sys.exit = CommandBaseTest.FakeExit()
    sys.stderr = CommandBaseTest.CaptureOutput()

    gcutil_logging.SetupLogging()
    self.assertRaises(command_base.CommandError,
                      command._ParseArgumentsAndFlags,
                      flag_values, command_line)

  def testSafetyPromptNo(self):
    flag_values = copy.deepcopy(FLAGS)
    command_line = ['mock_command']

    command = CommandBaseTest.MockSafetyCommand('mock_command', flag_values)
    args = command._ParseArgumentsAndFlags(flag_values, command_line)
    command.SetFlags(flag_values)

    mock_output = mock_api.MockOutput()
    mock_input = mock_api.MockInput('garbage\n\r')

    oldin = sys.stdin
    sys.stdin = mock_input
    oldout = sys.stdout
    sys.stdout = mock_output

    result = command._HandleSafetyPrompt(args)

    self.assertEqual(mock_output.GetCapturedText(),
                     'Take scary action? [y/N]\n>>> ')
    self.assertEqual(result, False)

    sys.stdin = oldin
    sys.stdout = oldout

  def testSafetyPromptForce(self):
    flag_values = copy.deepcopy(FLAGS)
    command_line = ['mock_command', '--force']

    command = CommandBaseTest.MockSafetyCommand('mock_command', flag_values)
    args = command._ParseArgumentsAndFlags(flag_values, command_line)
    command.SetFlags(flag_values)

    mock_output = mock_api.MockOutput()

    oldout = sys.stdout
    sys.stdout = mock_output

    result = command._HandleSafetyPrompt(args)

    sys.stdout = oldout

    self.assertEqual(result, True)
    self.assertEqual(mock_output.GetCapturedText(), '')

  def testPromptForChoicesWithOneDeprecatedItem(self):
    flag_values = copy.deepcopy(FLAGS)
    flag_values.project = 'p'

    command = command_base.GoogleComputeCommand('mock_command', flag_values)
    command.SetFlags(flag_values)

    mock_output = CommandBaseTest.CaptureOutput()

    oldout = sys.stdout
    sys.stdout = mock_output

    result = command._presenter.PromptForChoice(
        [{'name': 'item-1', 'deprecated': {'state': 'DEPRECATED'}}],
        'collection')

    self.assertEqual(
        mock_output.GetCapturedText(),
        'Selecting the only available collection: item-1\n')
    self.assertEqual(result, {'name': 'item-1', 'deprecated':
                              {'state': 'DEPRECATED'}})
    sys.stdout = oldout

  def testPromptForChoiceWithZone(self):
    """Test case to make sure the correct zone is used in prompt lists."""

    class MockCollectionApi(object):
      """Mock api that returns a single item with zone set."""

      def list(self, project=None, maxResults=None, filter=None,
               pageToken=None, zone=None):
        return mock_api.MockRequest(
            {'kind': 'compute#objectList',
             'id': 'projects/p/collection',
             'selfLink':
               'https://www.googleapis.com/compute/v1/projects/p/collection',
             'items': [{'name': 'item1', 'zone': zone}]})

    class MockPerZoneCommand(CommandBaseTest.ListMockCommandBase):
      """Mock command that exists only to define the --zone flag."""

      def __init__(self, name, flag_values):
        super(CommandBaseTest.ListMockCommandBase, self).__init__(
            name, flag_values)

        flags.DEFINE_string('zone',
                            None,
                            'The zone to use.',
                            flag_values=flag_values)

    flag_values = copy.deepcopy(FLAGS)
    expected_zone = 'z'
    flag_values.project = 'p'
    flag_values.service_version = 'v1beta15'

    command = MockPerZoneCommand('mock_command', flag_values)
    flag_values.zone = expected_zone
    command.SetFlags(flag_values)

    result = command._presenter.PromptForMachineType(
        MockCollectionApi(), for_test_auto_select=True)

    self.assertEqual(result, {'name': 'item1', 'zone': expected_zone})

  def testDetailOutput(self):
    flag_values = copy.deepcopy(FLAGS)
    flag_values.project = 'user'

    command = CommandBaseTest.MockDetailCommand('mock_command', flag_values)
    expected_output = (u'+-------------+-------------+\n'
                       '|  property   |    value    |\n'
                       '+-------------+-------------+\n'
                       '| name        | my-object-c |\n'
                       '| id          | 123         |\n'
                       '| description | Object C    |\n'
                       '| additional  | foo         |\n'
                       '+-------------+-------------+\n')
    mock_output = mock_api.MockOutput()

    oldout = sys.stdout
    sys.stdout = mock_output

    command.SetFlags(flag_values)
    result = command.Handle()
    command.PrintResult(result)

    sys.stdout = oldout

    self.assertEqual(mock_output.GetCapturedText(), expected_output)

  def testEmptyList(self):
    flag_values = copy.deepcopy(FLAGS)
    flag_values.project = 'user'

    class ListEmptyMockCommand(CommandBaseTest.ListMockCommand):
      def __init__(self, name, flag_values):
        super(ListEmptyMockCommand, self).__init__(name, flag_values)

      def Handle(self):
        return {'kind': 'cloud#objectsList'}

    command = ListEmptyMockCommand('empty_list', flag_values)
    expected_output = (u'+------+----+-------------+\n'
                       '| name | id | description |\n'
                       '+------+----+-------------+\n'
                       '+------+----+-------------+\n')
    mock_output = mock_api.MockOutput()

    oldout = sys.stdout
    sys.stdout = mock_output

    command.SetFlags(flag_values)
    result = command.Handle()
    command.PrintResult(result)

    sys.stdout = oldout

    self.assertEqual(mock_output.GetCapturedText(), expected_output)

  def testSortingNone(self):
    flag_values = copy.deepcopy(FLAGS)
    flag_values.project = 'user'

    command = CommandBaseTest.ListMockCommandBase('mock_command', flag_values)
    expected_output = (u'+-------------+-----+-------------+\n'
                       '|    name     | id  | description |\n'
                       '+-------------+-----+-------------+\n'
                       '| my-object-c | 123 | Object C    |\n'
                       '| my-object-a | 789 | Object A    |\n'
                       '| my-object-b | 456 | Object B    |\n'
                       '| my-object-d | 999 | Object D    |\n'
                       '+-------------+-----+-------------+\n')
    mock_output = mock_api.MockOutput()

    oldout = sys.stdout
    sys.stdout = mock_output

    command.SetFlags(flag_values)
    result = command.Handle()
    command.PrintResult(result)

    sys.stdout = oldout

    self.assertEqual(mock_output.GetCapturedText(), expected_output)

  def testSortingDefault(self):
    flag_values = copy.deepcopy(FLAGS)
    flag_values.project = 'user'

    command = CommandBaseTest.ListMockCommand('mock_command', flag_values)
    mock_output = mock_api.MockOutput()
    expected_output = (u'+-------------+-----+-------------+\n'
                       '|    name     | id  | description |\n'
                       '+-------------+-----+-------------+\n'
                       '| my-object-a | 789 | Object A    |\n'
                       '| my-object-b | 456 | Object B    |\n'
                       '| my-object-c | 123 | Object C    |\n'
                       '| my-object-d | 999 | Object D    |\n'
                       '+-------------+-----+-------------+\n')

    oldout = sys.stdout
    sys.stdout = mock_output

    command.SetFlags(flag_values)
    result = command.Handle()
    command.PrintResult(result)

    sys.stdout = oldout

    self.assertEqual(mock_output.GetCapturedText(), expected_output)

  def testSortingSpecifiedInAscendingOrder(self):
    flag_values = copy.deepcopy(FLAGS)
    flag_values.project = 'user'

    command = CommandBaseTest.ListMockCommand('mock_command', flag_values)
    mock_output = mock_api.MockOutput()

    flag_values.sort_by = 'id'

    expected_output = (u'+-------------+-----+-------------+\n'
                       '|    name     | id  | description |\n'
                       '+-------------+-----+-------------+\n'
                       '| my-object-c | 123 | Object C    |\n'
                       '| my-object-b | 456 | Object B    |\n'
                       '| my-object-a | 789 | Object A    |\n'
                       '| my-object-d | 999 | Object D    |\n'
                       '+-------------+-----+-------------+\n')

    oldout = sys.stdout
    sys.stdout = mock_output

    command.SetFlags(flag_values)
    result = command.Handle()
    command.PrintResult(result)

    sys.stdout = oldout

    self.assertEqual(mock_output.GetCapturedText(), expected_output)

  def testSortingSpecifiedInDescendingOrder(self):
    flag_values = copy.deepcopy(FLAGS)
    flag_values.project = 'user'

    command = CommandBaseTest.ListMockCommand('mock_command', flag_values)
    mock_output = mock_api.MockOutput()

    flag_values.sort_by = '-id'

    expected_output = (u'+-------------+-----+-------------+\n'
                       '|    name     | id  | description |\n'
                       '+-------------+-----+-------------+\n'
                       '| my-object-d | 999 | Object D    |\n'
                       '| my-object-a | 789 | Object A    |\n'
                       '| my-object-b | 456 | Object B    |\n'
                       '| my-object-c | 123 | Object C    |\n'
                       '+-------------+-----+-------------+\n')

    oldout = sys.stdout
    sys.stdout = mock_output

    command.SetFlags(flag_values)
    result = command.Handle()
    command.PrintResult(result)

    sys.stdout = oldout

    self.assertEqual(mock_output.GetCapturedText(), expected_output)

  def testGracefulHandlingOfInvalidDefaultSortField(self):

    class ListMockCommandWithBadDefaultSortField(
        CommandBaseTest.ListMockCommandBase):

      print_spec = command_base.ResourcePrintSpec(
          summary=(
              ('name', 'id'),
              ('id', 'number'),
              ('description', 'description')),
          detail=(
              ('name', 'id'),
              ('id', 'number'),
              ('description', 'description')),
          sort_by='bad-field-name')

      def __init__(self, name, flag_values):
        super(ListMockCommandWithBadDefaultSortField, self).__init__(
            name, flag_values)

    flag_values = copy.deepcopy(FLAGS)
    flag_values.project = 'user'

    command = ListMockCommandWithBadDefaultSortField(
        'mock_command', flag_values)

    # The output is expected to remain unsorted if the default sort
    # field is invalid.
    expected_output = (u'+-------------+-----+-------------+\n'
                       '|    name     | id  | description |\n'
                       '+-------------+-----+-------------+\n'
                       '| my-object-c | 123 | Object C    |\n'
                       '| my-object-a | 789 | Object A    |\n'
                       '| my-object-b | 456 | Object B    |\n'
                       '| my-object-d | 999 | Object D    |\n'
                       '+-------------+-----+-------------+\n')
    mock_output = mock_api.MockOutput()

    oldout = sys.stdout
    sys.stdout = mock_output

    command.SetFlags(flag_values)
    result = command.Handle()
    command.PrintResult(result)

    sys.stdout = oldout

    self.assertEqual(mock_output.GetCapturedText(), expected_output)

  def testVersionComparison(self):
    class MockCommand(CommandBaseTest.ListMockCommand):
      def __init__(self, name, flag_values):
        super(MockCommand, self).__init__(name, flag_values)

    flag_values = copy.deepcopy(FLAGS)

    command = MockCommand('mock_command', flag_values)
    command.supported_versions = ['v1beta2', 'v1beta3', 'v1beta4',
                                  'v1beta5', 'v1beta6']

    flag_values.service_version = 'v1beta4'
    command.SetFlags(flag_values)
    self.assertFalse(command._IsUsingAtLeastApiVersion('v1beta6'))
    self.assertFalse(command._IsUsingAtLeastApiVersion('v1beta5'))
    self.assertTrue(command._IsUsingAtLeastApiVersion('v1beta4'))
    self.assertTrue(command._IsUsingAtLeastApiVersion('v1beta2'))

    flag_values.service_version = 'v1beta6'
    command.SetFlags(flag_values)
    self.assertTrue(command._IsUsingAtLeastApiVersion('v1beta6'))
    self.assertTrue(command._IsUsingAtLeastApiVersion('v1beta5'))
    self.assertTrue(command._IsUsingAtLeastApiVersion('v1beta4'))
    self.assertTrue(command._IsUsingAtLeastApiVersion('v1beta2'))

  def testTracing(self):
    class MockComputeApi(object):
      def __init__(self, trace_calls):
        self._trace_calls = trace_calls

      def Disks(self):
        class MockDisksApi(object):
          def __init__(self, trace_calls):
            self._trace_calls = trace_calls

          def Insert(self, trace=None):
            if trace:
              self._trace_calls.append(trace)

        return MockDisksApi(self._trace_calls)

    # Expect no tracing if flag is not set.
    trace_calls = []
    compute = command_base.GoogleComputeCommand.WrapApiIfNeeded(
        MockComputeApi(trace_calls))
    compute.Disks().Insert()
    self.assertEqual(0, len(trace_calls))

    # Expect tracing if trace_token flag is set.
    trace_calls = []
    FLAGS.trace_token = 'THE_TOKEN'
    compute = command_base.GoogleComputeCommand.WrapApiIfNeeded(
        MockComputeApi(trace_calls))
    compute.Disks().Insert()
    self.assertEqual(1, len(trace_calls))
    self.assertEqual('token:THE_TOKEN', trace_calls[0])
    FLAGS.trace_token = ''


  def testWaitForOperation(self):
    complete_name = 'operation-complete'
    running_name = 'operation-running'
    pending_name = 'operation-pending'
    stuck_name = 'operation-stuck'

    base_operation = {'kind': 'cloud#operation',
                      'targetLink': ('https://www.googleapis.com/compute/'
                                     'v1beta100/projects/p/instances/i1'),
                      'operationType': 'insert',
                      'selfLink': ('https://www.googleapis.com/compute/'
                                   'v1beta100/projects/p/operations/op')}

    completed_operation = dict(base_operation)
    completed_operation.update({'name': complete_name,
                                'status': 'DONE'})
    running_operation = dict(base_operation)
    running_operation.update({'name': running_name,
                              'status': 'RUNNING'})
    pending_operation = dict(base_operation)
    pending_operation.update({'name': pending_name,
                              'status': 'PENDING'})
    stuck_operation = dict(base_operation)
    stuck_operation.update({'name': stuck_name,
                            'status': 'PENDING'})

    next_operation = {complete_name: completed_operation,
                      running_name: completed_operation,
                      pending_name: running_operation,
                      stuck_name: stuck_operation}


    class MockHttpResponse(object):
      def __init__(self, status, reason):
        self.status = status
        self.reason = reason

    class MockHttp(object):

      # pylint: disable=unused-argument
      def request(self_, url, method='GET', body=None, headers=None):
        response = MockHttpResponse(200, 'OK')
        data = '{ "kind": "compute#instance", "name": "i1" }'
        return response, data

    class MockCommand(command_base.GoogleComputeCommand):
      def __init__(self, name, flag_values):
        super(MockCommand, self).__init__(name, flag_values)

      def SetApi(self, api):
        pass

      def Handle(self):
        pass

      def CreateHttp(self):
        return MockHttp()

    class MockTimer(object):
      def __init__(self):
        self._current_time = 0

      def time(self):
        return self._current_time

      def sleep(self, time_to_sleep):
        self._current_time += time_to_sleep
        return self._current_time

    class LocalMockOperationsApi(object):
      def __init__(self):
        self._get_call_count = 0

      def GetCallCount(self):
        return self._get_call_count

      def get(self, project='unused project', operation='operation'):
        unused_project = project
        self._get_call_count += 1
        return mock_api.MockRequest(next_operation[operation])

    flag_values = copy.deepcopy(FLAGS)
    flag_values.sleep_between_polls = 1
    flag_values.max_wait_time = 30
    flag_values.service_version = 'v1beta15'
    flag_values.synchronous_mode = False
    flag_values.project = 'test'

    # Ensure a synchronous result returns immediately.
    timer = MockTimer()
    command = MockCommand('mock_command', flag_values)
    command.SetFlags(flag_values)
    command.SetApi(mock_api.MockApi())
    command._global_operations_api = LocalMockOperationsApi()
    diskResult = {'kind': 'cloud#disk'}
    result = command.WaitForOperation(
        flag_values.max_wait_time, flag_values.sleep_between_polls,
        timer, diskResult)
    self.assertEqual(0, command._global_operations_api.GetCallCount())

    # Ensure an asynchronous result loops until complete.
    timer = MockTimer()
    command = MockCommand('mock_command', flag_values)
    command.SetFlags(flag_values)
    command.SetApi(mock_api.MockApi())
    command._global_operations_api = LocalMockOperationsApi()
    print pending_operation
    result = command.WaitForOperation(
        flag_values.max_wait_time, flag_values.sleep_between_polls,
        timer, pending_operation)
    self.assertEqual(2, command._global_operations_api.GetCallCount())

    # Ensure an asynchronous result eventually times out
    timer = MockTimer()
    command = MockCommand('mock_command', flag_values)
    command.SetFlags(flag_values)
    command.SetApi(mock_api.MockApi())
    command._global_operations_api = LocalMockOperationsApi()
    result = command.WaitForOperation(
        flag_values.max_wait_time, flag_values.sleep_between_polls,
        timer, stuck_operation)
    self.assertEqual(30, command._global_operations_api.GetCallCount())
    self.assertEqual(result['status'], 'PENDING')

  def testBuildComputeApi(self):
    """Ensures that building of the API from the discovery succeeds."""
    flag_values = copy.deepcopy(FLAGS)
    command = command_base.GoogleComputeCommand('test_cmd', flag_values)
    command._BuildComputeApi(None)

  def testGetZone(self):
    zones = {
        'zone-a': {
            'kind': 'compute#zone',
            'id': '1',
            'creationTimestamp': '2011-07-27T20:04:06.171',
            'selfLink': (
                'https://googleapis.com/compute/v1/projects/p/zones/zone-a'),
            'name': 'zone-a',
            'description': 'Zone zone/a',
            'status': 'UP'},
        'zone-b': {
            'kind': 'compute#zone',
            'id': '2',
            'creationTimestamp': '2012-01-12T00:20:42.057',
            'selfLink': (
                'https://googleapis.com/compute/v1/projects/p/zones/zone-b'),
            'name': 'zone-b',
            'description': 'Zone zone/b',
            'status': 'UP',
            'maintenanceWindows': [
                {
                    'name': '2012-06-24-planned-outage',
                    'description': 'maintenance zone',
                    'beginTime': '2012-06-24T07:00:00.000',
                    'endTime': '2012-07-08T07:00:00.000'
                    }
                ]
            }
        }

    class MockCommand(command_base.GoogleComputeCommand):
      def __init__(self, name, flag_values):
        super(MockCommand, self).__init__(name, flag_values)

      def SetApi(self, api):
        pass

      def Handle(self):
        pass

    class MockZonesApi(object):

      def get(self, zone, **unused_kwargs):
        return mock_api.MockRequest(zones[zone])

      def list(self, *unused_args, **unused_kwargs):
        return mock_api.MockRequest({'items': [{'name': 'zone-a'}]})

    flag_values = copy.deepcopy(FLAGS)
    command = MockCommand('mock_command', flag_values)
    flag_values.project = 'p'
    command.SetFlags(flag_values)
    command._zones_api = MockZonesApi()

    self.assertEqual('zone-a', command._GetZone('zone-a'))
    self.assertEqual('zone-b', command._GetZone('zone-b'))
    self.assertEqual('zone-a', command._GetZone(None))

  def testGetNextMaintenanceStart(self):
    zone = {
        'kind': 'compute#zone',
        'name': 'zone',
        'maintenanceWindows': [
            {
                'name': 'january',
                'beginTime': '2013-01-01T00:00:00.000',
                'endTime': '2013-01-31T00:00:00.000'
                },
            {
                'name': 'march',
                'beginTime': '2013-03-01T00:00:00.000',
                'endTime': '2013-03-31T00:00:00.000'
                },
            ]
        }

    gnms = command_base.GoogleComputeCommand.GetNextMaintenanceStart
    start = gnms(zone, datetime.datetime(2012, 12, 1))
    self.assertEqual(start, datetime.datetime(2013, 1, 1))
    start = gnms(zone, datetime.datetime(2013, 2, 14))
    self.assertEqual(start, datetime.datetime(2013, 3, 1))
    start = gnms(zone, datetime.datetime(2013, 3, 15))
    self.assertEqual(start, datetime.datetime(2013, 3, 1))

  def testGetZoneForResource(self):
    flag_values = copy.deepcopy(FLAGS)
    expected_project = 'google'
    flag_values.project = expected_project
    flag_values.service_version = 'v1beta15'

    class MockCommand(command_base.GoogleComputeCommand):

      resource_collection_name = 'foos'

      def __init__(self, name, flag_values):
        super(MockCommand, self).__init__(name, flag_values)
        flags.DEFINE_string('zone',
                            None,
                            'Zone name.',
                            flag_values=flag_values)
        self.params = None

      def RunWithFlagsAndPositionalArgs(self, flag_values, pos_arg_values):
        if self._flags != flag_values:
          raise RuntimeError('Flags mismatch')
        self.Handle(*pos_arg_values)

      def Handle(self, param1, param2):
        self.params = (param1, param2)
        return None

    class MockApi(object):
      list_response = None

      def __init__(self):
        pass

      def list(self, **kwargs):
        self.list_parameters = kwargs
        return self.list_response

    class LocalMockZonesApi(object):

      # pylint: disable=unused-argument
      def list(self, project='unused project', maxResults='unused',
               filter='unused'):
        return mock_api.MockRequest({'items': [{'name': 'zone1'}]})

    command = MockCommand('mock_command', flag_values)
    command._zones_api = LocalMockZonesApi()
    api = MockApi()
    command.SetFlags(flag_values)

    # Project-qualified name.
    self.assertEqual(
        command.GetZoneForResource(None, 'projects/foo/zones/bar'), 'bar')

    # Special 'global' zone.
    flag_values.zone = 'global'
    command.SetFlags(flag_values)
    self.assertEqual(
        command.GetZoneForResource(None, command_base.GLOBAL_SCOPE_NAME),
        None)

    # Zone name explicitly set.
    flag_values.zone = 'explicitly-set-zone'
    command.SetFlags(flag_values)
    self.assertEqual(
        command.GetZoneForResource(None, 'some-resource'),
        'explicitly-set-zone')


  def testGetUsageWithPositionalArgs(self):

    class MockCommand(command_base.GoogleComputeCommand):
      positional_args = '<arg-1> ... <arg-n>'

    flag_values = copy.deepcopy(FLAGS)
    command = MockCommand('mock_command', flag_values)
    self.assertTrue(command._GetUsage().endswith(
        ' [--global_flags] mock_command [--command_flags] <arg-1> ... <arg-n>'))

  def testGetUsageWithNoPositionalArgs(self):

    class MockCommand(command_base.GoogleComputeCommand):
      pass

    flag_values = copy.deepcopy(FLAGS)
    command = MockCommand('mock_command', flag_values)
    self.assertTrue(command._GetUsage().endswith(
        ' [--global_flags] mock_command [--command_flags]'))


  def testGoogleComputeListCommandPerZone(self):
    flag_values = copy.deepcopy(FLAGS)
    expected_project = 'foo'
    flag_values.project = expected_project
    flag_values.service_version = 'v1beta14'

    object_a = {'description': 'Object A',
                'id': 'projects/user/zones/a/objects/my-object-a',
                'kind': 'cloud#object'}
    object_b = {'description': 'Object B',
                'id': 'projects/user/zones/b/objects/my-object-b',
                'kind': 'cloud#object'}
    list_a = {'items': [object_a],
              'kind': 'cloud#objectList'}
    list_b = {'items': [object_b],
              'kind': 'cloud#objectList'}
    list_all = {'items': [object_a, object_b],
                'kind': 'cloud#objectList'}

    class LocalMockZonesApi(object):

      # pylint: disable=unused-argument
      def list(self, project='unused project', maxResults='unused',
               filter='unused'):
        return mock_api.MockRequest({'items': [{'name': 'a'},
                                               {'name': 'b'}]})

    class ZoneListMockCommand(CommandBaseTest.ListMockCommandBase):
      """A list mock command that represents a zone-scoped collection."""

      def IsZoneLevelCollection(self):
        return True

      def IsGlobalLevelCollection(self):
        return False

      def __init__(self, name, flag_values):
        super(CommandBaseTest.ListMockCommandBase, self).__init__(name,
                                                                  flag_values)
        flags.DEFINE_string('zone',
                            None,
                            'The zone to list.',
                            flag_values=flag_values)

      def ListZoneFunc(self):

        # pylint: disable=unused-argument
        def Func(project=None, maxResults=None, filter=None, pageToken=None,
                 zone=None):
          if zone == 'a':
            return mock_api.MockRequest(list_a)
          else:
            return mock_api.MockRequest(list_b)

        return Func

    command = ZoneListMockCommand('mock_command', flag_values)
    command._zones_api = LocalMockZonesApi()

    # Test single zone
    flag_values.zone = 'a'
    command.SetFlags(flag_values)
    self.assertEqual(list_a, command.Handle())

    # Test all zones
    flag_values.zone = None
    command.SetFlags(flag_values)
    self.assertEqual(list_all, command.Handle())

  def testGoogleComputeListCommandAggregated(self):
    flag_values = copy.deepcopy(FLAGS)
    expected_project = 'foo'
    flag_values.project = expected_project
    flag_values.service_version = 'v1beta15'

    object_a = {'description': 'Object A',
                'id': 'projects/user/zones/a/objects/my-object-a',
                'kind': 'cloud#object'}
    object_b = {'description': 'Object B',
                'id': 'projects/user/zones/b/objects/my-object-b',
                'kind': 'cloud#object'}
    object_global = {'description': 'Object Global',
                     'id': 'projects/user/objects/global/my-object-global',
                     'kind': 'cloud#object'}

    aggregated_list = {'kind': 'cloud#objectAggregatedList',
                       'items': {
                           'a': {
                               'objects': [object_a]
                               },
                           'b': {
                               'objects': [object_b]
                               },
                           'c': {
                               'warning': {
                                   'code': 'UNREACHABLE',
                                   'message': 'c is unreachable',
                                   }
                               },
                           'global': {
                               'objects': [object_global]
                               },
                           },
                       }

    next_page_token = 'give_me_page_2'
    aggregated_list_page_1 = {'kind': 'cloud#objectAggregatedList',
                              'items': {
                                  'a': {
                                      'objects': [object_a]
                                      },
                                  'b': {
                                      'warning': {
                                          'code': 'NO_RESULTS_ON_PAGE',
                                          'message': 'Nothing to see here.',
                                          }
                                      },
                                  'c': {
                                      'warning': {
                                          'code': 'UNREACHABLE',
                                          'message': 'c is unreachable',
                                          }
                                      },
                                  'global': {
                                      'objects': [object_global]
                                      },
                                  },
                              'nextPageToken': next_page_token,
                              }
    aggregated_list_page_2 = {'kind': 'cloud#objectAggregatedList',
                              'items': {
                                  'a': {
                                      'warning': {
                                          'code': 'NO_RESULTS_ON_PAGE',
                                          'message': 'Nothing to see here.',
                                          }
                                      },
                                  'b': {
                                      'objects': [object_b]
                                      },
                                  'c': {
                                      'warning': {
                                          'code': 'UNREACHABLE',
                                          'message': 'c is unreachable',
                                          }
                                      },
                                  'global': {
                                      'warning': {
                                          'code': 'NO_RESULTS_ON_PAGE',
                                          'message': 'Nothing to see here.',
                                          }
                                      },
                                  },
                              }

    class AggregatedListMockCommand(CommandBaseTest.ListMockCommandBase):
      """A mock list command that represents an aggregated collection."""

      resource_collection_name = 'objects'

      def IsZoneLevelCollection(self):
        return True

      def IsGlobalLevelCollection(self):
        return True

      def __init__(self, name, flag_values):
        super(CommandBaseTest.ListMockCommandBase, self).__init__(name,
                                                                  flag_values)

      def ListAggregatedFunc(self):

        # pylint: disable=unused-argument
        def Func(project=None, maxResults=None, filter=None, pageToken=None):
          if pageToken is next_page_token:
            return mock_api.MockRequest(aggregated_list_page_2)
          return mock_api.MockRequest(aggregated_list_page_1)
        return Func

    command = AggregatedListMockCommand('mock_command', flag_values)

    command.SetFlags(flag_values)
    self.assertEqual(aggregated_list, command.Handle())

  def testGoogleComputeListCommandZoneAndGlobal(self):
    flag_values = copy.deepcopy(FLAGS)
    expected_project = 'foo'
    flag_values.project = expected_project
    flag_values.service_version = 'v1beta14'

    object_a = {'description': 'Object A',
                'id': 'projects/user/zones/a/objects/my-object-a',
                'kind': 'cloud#object'}
    object_b = {'description': 'Object B',
                'id': 'projects/user/zones/b/objects/my-object-b',
                'kind': 'cloud#object'}
    object_c = {'description': 'Object C',
                'id': 'projects/user/objects/my-object-c',
                'kind': 'cloud#object'}
    list_global = {'items': [object_c],
                   'kind': 'cloud#objectList'}
    list_a = {'items': [object_a],
              'kind': 'cloud#objectList'}
    list_b = {'items': [object_b],
              'kind': 'cloud#objectList'}
    list_all = {'items': [object_a, object_b, object_c],
                'kind': 'cloud#objectList'}

    class LocalMockZonesApi(object):

      # pylint: disable=unused-argument
      def list(self, project='unused project', maxResults='unused',
               filter='unused'):
        return mock_api.MockRequest({'items': [{'name': 'a'},
                                               {'name': 'b'}]})

    class GlobalAndZoneListMockCommand(CommandBaseTest.ListMockCommandBase):
      """A list mock command that represents a zone-scoped collection."""

      def IsZoneLevelCollection(self):
        return True

      def IsGlobalLevelCollection(self):
        return True

      def __init__(self, name, flag_values):
        super(CommandBaseTest.ListMockCommandBase, self).__init__(name,
                                                                  flag_values)
        flags.DEFINE_string('zone',
                            None,
                            'The zone to list.',
                            flag_values=flag_values)

      def ListZoneFunc(self):
        # pylint: disable=unused-argument
        # pylint: disable=redefined-builtin
        def Func(project=None, maxResults=None, filter=None, pageToken=None,
                 zone=None):
          if zone == 'a':
            return mock_api.MockRequest(list_a)
          else:
            return mock_api.MockRequest(list_b)
        return Func

      def ListFunc(self):

        # pylint: disable=unused-argument
        def Func(project=None, maxResults=None, filter=None, pageToken=None):
          return mock_api.MockRequest(list_global)
        return Func

    command = GlobalAndZoneListMockCommand('mock_command', flag_values)
    command._zones_api = LocalMockZonesApi()

    # Test single zone
    flag_values['zone'].value = 'a'
    flag_values['zone'].present = 1
    command.SetFlags(flag_values)
    self.assertEqual(list_a, command.Handle())

    # Test 'global' zone
    flag_values.zone = 'global'
    command.SetFlags(flag_values)
    self.assertEqual(list_global, command.Handle())

    # Test all
    flag_values['zone'].value = None
    flag_values['zone'].present = 0
    command.SetFlags(flag_values)
    self.assertEqual(list_all, command.Handle())

  def testOperationPrintSpec(self):
    spec = command_base.GoogleComputeCommand.operation_print_spec
    spec_v1beta15 = (
        command_base.GoogleComputeCommand.operation_print_spec_v1beta15)

    # Summary
    self.assertEqual(set([('region', 'region')]),
                     set(spec.summary) ^ set(spec_v1beta15.summary))
    # Detail
    self.assertEqual(set([('region', 'region')]),
                     set(spec.detail) ^ set(spec_v1beta15.detail))
    # Sort By
    self.assertEqual(spec.sort_by, spec_v1beta15.sort_by)

  def testOperationPrintSpecVersions(self):
    class MockCommand(CommandBaseTest.ListMockCommand):
      def __init__(self, name, flag_values):
        super(MockCommand, self).__init__(name, flag_values)

    flag_values = copy.deepcopy(FLAGS)

    command = MockCommand('mock_command', flag_values)
    command.supported_versions = ['v1beta14', 'v1beta15']

    flag_values.service_version = 'v1beta14'
    command.SetFlags(flag_values)
    self.assertTrue(
        command_base.GoogleComputeCommand.operation_print_spec is
        command.GetOperationPrintSpec())

    flag_values.service_version = 'v1beta15'
    command.SetFlags(flag_values)
    self.assertTrue(
        command_base.GoogleComputeCommand.operation_print_spec_v1beta15 is
        command.GetOperationPrintSpec())

  def testGoogleComputeListCommandZoneRegionGlobal(self):
    flag_values = copy.deepcopy(FLAGS)
    expected_project = 'foo'
    flag_values.project = expected_project
    flag_values.service_version = 'v1beta14'

    def CreateObjects(scope):
      return (
          {'description': 'Object A - %s' % scope,
           'id': 'projects/user/%s/object-a' % scope,
           'kind': 'cloud#object'},
          {'description': 'Object B - %s' % scope,
           'id': 'projects/user/%s/object-b' % scope,
           'kind': 'cloud#object'}
          )

    def CreateList(*elements):
      return {'items': elements, 'kind': 'cloud#objectList'}

    # Global objects
    global_object_a, global_object_b = CreateObjects('global')
    global_list = CreateList(global_object_a, global_object_b)
    # Zone M
    zone_m_object_a, zone_m_object_b = CreateObjects('zones/zone-m')
    zone_m_list = CreateList(zone_m_object_a, zone_m_object_b)
    # Zone N
    zone_n_object_a, zone_n_object_b = CreateObjects('zones/zone-n')
    zone_n_list = CreateList(zone_n_object_a, zone_n_object_b)
    # Region R
    region_r_object_a, region_r_object_b = CreateObjects('regions/region-r')
    region_r_list = CreateList(region_r_object_a, region_r_object_b)
    # Region S
    region_s_object_a, region_s_object_b = CreateObjects('regions/region-s')
    region_s_list = CreateList(region_s_object_a, region_s_object_b)

    class LocalMockZonesApi(object):
      def list(self, project='unused project', maxResults='unused',
               filter='unused'):
        return mock_api.MockRequest({'items': [{'name': 'zone-m'},
                                               {'name': 'zone-n'}]})

    class LocalMockRegionsApi(object):
      def list(self, project='unused project', maxResults='unused',
               filter='unused'):
        return mock_api.MockRequest({'items': [{'name': 'region-r'},
                                               {'name': 'region-s'}]})

    class ListMockCommand(CommandBaseTest.ListMockCommandBase):
      """A list mock command that represents a multi-scoped collection."""

      def IsZoneLevelCollection(self):
        return True

      def IsGlobalLevelCollection(self):
        return True

      def IsRegionLevelCollection(self):
        return True

      def __init__(self, name, flag_values):
        super(CommandBaseTest.ListMockCommandBase, self).__init__(name,
                                                                  flag_values)
        flags.DEFINE_bool(
            'global',
            None,
            'Operations in global scope.',
            flag_values=flag_values)
        flags.DEFINE_string(
            'region',
            None,
            'The name of the region scope for region operations.',
            flag_values=flag_values)
        flags.DEFINE_string(
            'zone',
            None,
            'The name of the zone scope for zone operations.',
            flag_values=flag_values)

      def ListZoneFunc(self):
        def Func(project=None, maxResults=None, filter=None, pageToken=None,
                 zone=None):
          assert zone in ('zone-m', 'zone-n')
          return mock_api.MockRequest(
              zone_m_list if zone == 'zone-m' else zone_n_list)
        return Func

      def ListRegionFunc(self):
        def Func(project=None, maxResults=None, filter=None, pageToken=None,
                 region=None):
          assert region in ('region-r', 'region-s')
          return mock_api.MockRequest(
              region_r_list if region == 'region-r' else region_s_list)
        return Func

      def ListFunc(self):
        def Func(project=None, maxResults=None, filter=None, pageToken=None):
          return mock_api.MockRequest(global_list)
        return Func

    command = ListMockCommand('mock_command', flag_values)
    command.SetFlags(flag_values)
    command._zones_api = LocalMockZonesApi()
    command._regions_api = LocalMockRegionsApi()

    def SetFlag(name, value):
      flag_values[name].value = value
      flag_values[name].present = 1

    def ClearFlag(name):
      flag_values[name].value = flag_values[name].default
      flag_values[name].present = 0

    # Run without args v1beta14. Should list all zones and global level.
    SetFlag('service_version', 'v1beta14')
    self.assertEqual(
        {'kind': 'cloud#objectList',
         'items': [zone_m_object_a, zone_m_object_b,
                   zone_n_object_a, zone_n_object_b,
                   global_object_a, global_object_b]},
        command.Handle())

    # Run without args v1beta15. Should list all zones, all regions and also
    # global level.
    SetFlag('service_version', 'v1beta15')
    self.assertEqual(
        {'kind': 'cloud#objectList',
         'items': [zone_m_object_a, zone_m_object_b,
                   zone_n_object_a, zone_n_object_b,
                   region_r_object_a, region_r_object_b,
                   region_s_object_a, region_s_object_b,
                   global_object_a, global_object_b]},
        command.Handle())

    # Ask for a specific zone. Should only list that zone.
    SetFlag('zone', 'zone-n')
    self.assertEqual(
        {'kind': 'cloud#objectList',
         'items': [zone_n_object_a, zone_n_object_b]},
        command.Handle())

    # Ask for a specific region. Should only list that region.
    ClearFlag('zone')
    SetFlag('region', 'region-s')
    self.assertEqual(
        {'kind': 'cloud#objectList',
         'items': [region_s_object_a, region_s_object_b]},
        command.Handle())

    # Ask for global only. Should only list global objects.
    ClearFlag('region')
    SetFlag('global', True)
    self.assertEqual(
        {'kind': 'cloud#objectList',
         'items': [global_object_a, global_object_b]},
        command.Handle())

    # Ask for zone and region. Should only list those.
    SetFlag('zone', 'zone-m')
    SetFlag('region', 'region-r')
    ClearFlag('global')
    self.assertEqual(
        {'kind': 'cloud#objectList',
         'items': [zone_m_object_a, zone_m_object_b,
                   region_r_object_a, region_r_object_b]},
        command.Handle())

    # Ask for zone and global.
    SetFlag('zone', 'zone-n')
    SetFlag('global', True)
    ClearFlag('region')
    self.assertEqual(
        {'kind': 'cloud#objectList',
         'items': [zone_n_object_a, zone_n_object_b,
                   global_object_a, global_object_b]},
        command.Handle())

    # Ask for region and global.
    ClearFlag('zone')
    SetFlag('region', 'region-s')
    SetFlag('global', True)
    self.assertEqual(
        {'kind': 'cloud#objectList',
         'items': [region_s_object_a, region_s_object_b,
                   global_object_a, global_object_b]},
        command.Handle())

    # Specify global, zone and region. Should only return data from specified
    # collections (not all zones, regions, only specified ones).
    SetFlag('zone', 'zone-m')
    SetFlag('region', 'region-r')
    SetFlag('global', True)
    self.assertEqual(
        {'kind': 'cloud#objectList',
         'items': [zone_m_object_a, zone_m_object_b,
                   region_r_object_a, region_r_object_b,
                   global_object_a, global_object_b]},
        command.Handle())

    # Deprecated behavior. Specify global zone.
    SetFlag('zone', 'global')
    ClearFlag('region')
    ClearFlag('global')
    self.assertEqual(
        {'kind': 'cloud#objectList',
         'items': [global_object_a, global_object_b]},
        command.Handle())

    # Deprecated behavior. Specify global zone and --global.
    # Get data only once.
    SetFlag('zone', 'global')
    SetFlag('global', True)
    ClearFlag('region')
    self.assertEqual(
        {'kind': 'cloud#objectList',
         'items': [global_object_a, global_object_b]},
        command.Handle())

  def _DoTestGetScopeFromSelfLink(self, version):
    class MockCommand(command_base.GoogleComputeCommand):
      pass

    base = 'https://www.googleapis.com/compute/'

    flag_values = copy.deepcopy(FLAGS)
    flag_values.api_host = 'https://www.googleapis.com/'
    flag_values.service_version = version

    command = MockCommand('mock_command', flag_values)
    command.SetFlags(flag_values)

    tests = (
        (base + 'v1beta14/projects/my-project/global/networks/net',
         ('global', '')),

        (base + 'v1beta14/projects/my-project/zones/zone1/instances/inst',
         ('zones', 'zone1')),

        (base + 'v1beta14/projects/my-project/zones/zone2',
         ('zones', 'zone2')),

        # No suffix
        ('https://www.googleapis.com/',
         (None, None)),

        # just base URL
        (base,
         (None, None)),

        # missing projects
        (base + 'v1beta14/global/networks/net',
         (None, None)),

        # missing project
        (base + 'v1beta14/projects/global/networks/network',
         (None, None)),

        (base + 'v1beta15/projects/my-project/regions/region1/ips/ip',
         ('regions', 'region1')),

        # bad regions
        (base + 'v1beta15/projects/my-project/regins/region1/ips/ip',
         (None, None)),
    )

    for url, result in tests:
      scope = command._GetScopeFromSelfLink(url)
      error = ('Extracting scope from selfLink \'%s\' failed\n'
               '%s != %s') % (url, result, scope)
      self.assertEqual(result, scope, error)

  def testGetScopeFromSelfLink(self):
    for version in command_base.SUPPORTED_VERSIONS:
      self._DoTestGetScopeFromSelfLink(version)

  def testErrorInResultList(self):
    class MockCommand(command_base.GoogleComputeCommand):
      pass

    flag_values = copy.deepcopy(FLAGS)
    command = MockCommand('mock_command', flag_values)
    command.SetFlags(flag_values)

    self.assertFalse(command._ErrorsInResultList(None))
    self.assertFalse(command._ErrorsInResultList([]))

    operation = {
        'kind': 'compute#operation',
        'id': '9811220201106278825',
        'name': 'my-operation',
        'operationType': 'insert',
        'progress': 100,
        'selfLink': ('https://www.googleapis.com/compute/v1beta15/projects/'
                     'project/zones/my-zone/operations/my-operation'),
        'status': 'DONE'
        }

    self.assertTrue(command.IsResultAnOperation(operation))
    self.assertFalse(command._ErrorsInResultList([operation]))
    self.assertFalse(command._ErrorsInResultList([operation] * 10))

    error_operation = {
        'kind': 'compute#operation',
        'id': '9811220201106278825',
        'name': 'my-operation',
        'operationType': 'insert',
        'progress': 100,
        'selfLink': ('https://www.googleapis.com/compute/v1beta15/projects/'
                     'my-project/zones/my-zone/operations/my-operation'),
        'status': 'DONE',
        'error': {
            'errors': [{
                'code': 'RESOURCE_ALREADY_EXISTS',
                'message': ('The resource projects/my-project/instances/'
                            'my-instance already exists')
                }]
            }
        }

    self.assertTrue(command.IsResultAnOperation(error_operation))
    self.assertTrue(command._ErrorsInResultList([error_operation]))
    self.assertTrue(command._ErrorsInResultList(
        [operation] * 10 + [error_operation] + [operation] * 10))

  def testPresenterPresentElement(self):

    class MockCommand(command_base.GoogleComputeCommand):
      def __init__(self, name, flag_values):
        super(command_base.GoogleComputeCommand, self).__init__(
            name, flag_values)

        flags.DEFINE_string('zone',
                            None,
                            'The zone to use.',
                            flag_values=flag_values)

    flag_values = copy.deepcopy(FLAGS)
    flag_values.project = 'myproject'
    flag_values.api_host = 'https://www.googleapis.com/'
    flag_values.service_version = 'v1beta15'

    command = MockCommand('mock_command', flag_values)
    command.SetFlags(flag_values)
    presenter = command._presenter

    self.assertEquals(
        'us-central1-a/machineTypes/n1-standard-2-d',
        presenter.PresentElement(
            'https://www.googleapis.com/compute/v1beta15/projects/myproject'
            '/zones/us-central1-a/machineTypes/n1-standard-2-d'))

    #
    # Top level resource types.
    #
    self.assertEquals(
        'europe-west1-a',
        presenter.PresentElement(
            'https://www.googleapis.com/compute/v1beta15/projects/myproject'
            '/zones/europe-west1-a'))

    #
    # Global resource types.
    #

    # Image in your own project returns 'imagename'. (Global resource type).
    self.assertEquals(
        'imagename',
        presenter.PresentElement(
            'https://www.googleapis.com/compute/v1beta15/projects/myproject'
            '/global/images/imagename'))

    # Image in some other project returns reasonable path.
    self.assertEquals(
        'projects/yourproject/global/images/imagename',
        presenter.PresentElement(
            'https://www.googleapis.com/compute/v1beta15/projects/yourproject'
            '/global/images/imagename'))

    #
    # Zone resource types.
    #
    flag_values.zone = 'europe-west1-a'
    command.SetFlags(flag_values)

    # Truncate the type if zone is specified.
    self.assertEquals(
        'us-central1-a/machineTypes/n1-standard-2-d',
        presenter.PresentElement(
            'https://www.googleapis.com/compute/v1beta15/projects/myproject'
            '/zones/us-central1-a/machineTypes/n1-standard-2-d'))

    self.assertEquals(
        'us-central1-a',
        presenter.PresentElement(
            'https://www.googleapis.com/compute/v1beta15/projects/myproject'
            '/zones/us-central1-a'))

    # Truncate the zone and type if zone is specified.
    self.assertEquals(
        'n1-standard-2-d',
        presenter.PresentElement(
            'https://www.googleapis.com/compute/v1beta15/projects/myproject'
            '/zones/europe-west1-a/machineTypes/n1-standard-2-d'))

    # If the user specifies a long-form zone, it still works.
    flag_values.zone = (
        'https://www.googleapis.com/compute/v1beta15/projects/myproject'
        '/zones/europe-west1-a')
    command.SetFlags(flag_values)

    self.assertEquals(
        'n1-standard-2-d',
        presenter.PresentElement(
            'https://www.googleapis.com/compute/v1beta15/projects/myproject'
            '/zones/europe-west1-a/machineTypes/n1-standard-2-d'))

  def testPresenterPresentRegionElement(self):

    class MockCommand(command_base.GoogleComputeCommand):
      def __init__(self, name, flag_values):
        super(command_base.GoogleComputeCommand, self).__init__(
            name, flag_values)

        flags.DEFINE_string('region',
                            None,
                            'The zone to use.',
                            flag_values=flag_values)

    flag_values = copy.deepcopy(FLAGS)
    flag_values.project = 'myproject'
    flag_values.api_host = 'https://www.googleapis.com/'
    flag_values.service_version = 'v1beta15'

    command = MockCommand('mock_command', flag_values)
    command.SetFlags(flag_values)
    presenter = command._presenter

    self.assertEquals(
        'my-region/addresses/my-address',
        presenter.PresentElement(
            'https://www.googleapis.com/compute/v1beta15/projects/myproject'
            '/regions/my-region/addresses/my-address'))

    #
    # Top level resource types.
    #
    self.assertEquals(
        'europe-west',
        presenter.PresentElement(
            'https://www.googleapis.com/compute/v1beta15/projects/myproject'
            '/regions/europe-west'))

    #
    # Region resource types.
    #
    flag_values.region = 'europe-west'
    command.SetFlags(flag_values)

    # Truncate the type if region is specified.
    self.assertEquals(
        'us-central/addresses/my-address',
        presenter.PresentElement(
            'https://www.googleapis.com/compute/v1beta15/projects/myproject'
            '/regions/us-central/addresses/my-address'))

    self.assertEquals(
        'us-central',
        presenter.PresentElement(
            'https://www.googleapis.com/compute/v1beta15/projects/myproject'
            '/regions/us-central'))

    # Truncate the region and type if region is specified.
    self.assertEquals(
        'my-address',
        presenter.PresentElement(
            'https://www.googleapis.com/compute/v1beta15/projects/myproject'
            '/regions/europe-west/addresses/my-address'))

    # If the user specifies a long-form region, it still works.
    flag_values.region = (
        'https://www.googleapis.com/compute/v1beta15/projects/myproject'
        '/regions/europe-west')
    command.SetFlags(flag_values)

    self.assertEquals(
        'my-address',
        presenter.PresentElement(
            'https://www.googleapis.com/compute/v1beta15/projects/myproject'
            '/regions/europe-west/addresses/my-address'))


if __name__ == '__main__':
  unittest.main()
