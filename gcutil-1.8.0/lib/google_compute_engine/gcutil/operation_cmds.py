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

"""Commands for interacting with Google Compute Engine operations."""



from google.apputils import appcommands
import gflags as flags

from gcutil import command_base
from gcutil import gcutil_logging


FLAGS = flags.FLAGS
LOGGER = gcutil_logging.LOGGER


class OperationCommand(command_base.GoogleComputeCommand):
  """Base command for working with the operations collection.

  Attributes:
    print_spec: A specification describing how to print Operation resources.
    resource_collection_name: The name of the REST API collection handled by
        this command type.
  """

  print_spec = command_base.GoogleComputeCommand.operation_print_spec
  print_spec_v1beta15 = (
      command_base.GoogleComputeCommand.operation_print_spec_v1beta15)

  resource_collection_name = 'operations'

  def __init__(self, name, flag_values):
    super(OperationCommand, self).__init__(name, flag_values)
    flags.DEFINE_bool('global',
                      None,
                      'Operations in global scope.',
                      flag_values=flag_values)
    flags.DEFINE_string('region',
                        None,
                        'The name of the region scope for region operations.',
                        flag_values=flag_values)
    flags.DEFINE_string('zone',
                        None,
                        'The name of the zone scope for zone operations.',
                        flag_values=flag_values)

  def GetPrintSpec(self):
    if self._IsUsingAtLeastApiVersion('v1beta15'):
      return self.print_spec_v1beta15
    return self.print_spec

  def SetApi(self, api):
    """Set the Google Compute Engine API for the command.

    Args:
      api: The Google Compute Engine API used by this command.
    """
    self._zones_api = api.zones()

    if self._IsUsingAtLeastApiVersion('v1beta15'):
      self._regions_api = api.regions()
      self._region_operations_api = api.regionOperations()
    if self._IsUsingAtLeastApiVersion('v1beta14'):
      self._zone_operations_api = api.zoneOperations()
      self._global_operations_api = api.globalOperations()
    else:
      self._global_operations_api = api.operations()


class GetOperation(OperationCommand):
  """Retrieve an operation resource."""

  positional_args = '<operation-name>'

  def Handle(self, operation_name):
    """Get the specified operation.

    Args:
      operation_name: The name of the operation to get.

    Returns:
      The json formatted object resulting from retrieving the operation
      resource.
    """
    # Force asynchronous mode so the caller doesn't wait for this operation
    # to complete before returning.
    self._flags.synchronous_mode = False

    kwargs = {}
    if self._IsUsingAtLeastApiVersion('v1beta14') and self._flags.zone:
      if self._flags.zone == command_base.GLOBAL_SCOPE_NAME:
        LOGGER.warn(
            '--zone \'%s\' flag is deprecated; use --global instead' %
            command_base.GLOBAL_SCOPE_NAME)
        method = self._global_operations_api.get
      else:
        method = self._zone_operations_api.get
        kwargs['zone'] = self._flags.zone
    elif self._IsUsingAtLeastApiVersion('v1beta15') and self._flags.region:
      method = self._region_operations_api.get
      kwargs['region'] = self._flags.region
    else:
      method = self._global_operations_api.get

    request = method(
        project=self._project,
        operation=self.DenormalizeResourceName(operation_name),
        **kwargs)

    return request.execute()


class DeleteOperation(OperationCommand):
  """Delete one or more operations."""

  positional_args = '<operation-name-1> ... <operation-name-n>'
  safety_prompt = 'Delete operation'

  def Handle(self, *operation_names):
    """Delete the specified operations.

    Args:
      *operation_names: The names of the operations to delete.

    Returns:
      Tuple (results, exceptions) - results of deleting the operations.
    """
    requests = []
    kwargs = {}

    if self._IsUsingAtLeastApiVersion('v1beta14') and self._flags.zone:
      if self._flags.zone == command_base.GLOBAL_SCOPE_NAME:
        LOGGER.warn(
            '--zone \'%s\' flag is deprecated; use --global instead' %
            command_base.GLOBAL_SCOPE_NAME)
        method = self._global_operations_api.delete
      else:
        method = self._zone_operations_api.delete
        kwargs['zone'] = self._flags.zone
    elif self._IsUsingAtLeastApiVersion('v1beta15') and self._flags.region:
      method = self._region_operations_api.delete
      kwargs['region'] = self._flags.region
    else:
      method = self._global_operations_api.delete

    for operation_name in operation_names:
      requests.append(
          method(
              project=self._project,
              operation=self.DenormalizeResourceName(operation_name),
              **kwargs))

    _, exceptions = self.ExecuteRequests(requests)
    return '', exceptions


class ListOperations(OperationCommand, command_base.GoogleComputeListCommand):
  """List the operations for a project."""

  is_global_level_collection = True
  is_zone_level_collection = True

  def IsZoneLevelCollection(self):
    return True

  def IsRegionLevelCollection(self):
    return True

  def IsGlobalLevelCollection(self):
    return True

  def __init__(self, name, flag_values):
    super(ListOperations, self).__init__(name, flag_values)

  def ListFunc(self):
    """Returns the function for listing global operations."""
    return self._global_operations_api.list

  def ListRegionFunc(self):
    if self._IsUsingAtLeastApiVersion('v1beta15'):
      return self._region_operations_api.list
    else:
      return self._global_operations_api.list

  def ListZoneFunc(self):
    """Returns the function for listing operations in a zone."""
    if self._IsUsingAtLeastApiVersion('v1beta14'):
      return self._zone_operations_api.list
    return self._global_operations_api.list

  def ListAggregatedFunc(self):
    """Returns the function for listing operations across all scopes."""
    if self._IsUsingAtLeastApiVersion('v1beta15'):
      return self._global_operations_api.aggregatedList


def AddCommands():
  appcommands.AddCmd('getoperation', GetOperation)
  appcommands.AddCmd('deleteoperation', DeleteOperation)
  appcommands.AddCmd('listoperations', ListOperations)
