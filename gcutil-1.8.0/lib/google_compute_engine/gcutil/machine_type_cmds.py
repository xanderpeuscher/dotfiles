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

"""Commands for interacting with Google Compute Engine machine types."""




from google.apputils import appcommands
import gflags as flags

from gcutil import command_base


FLAGS = flags.FLAGS



class MachineTypeCommand(command_base.GoogleComputeCommand):
  """Base command for working with the machine types collection."""

  print_spec = command_base.ResourcePrintSpec(
      summary=(
          ('name', 'name'),
          ('description', 'description'),
          ('zone', 'zone'),
          ('cpus', 'guestCpus'),
          ('memory-mb', 'memoryMb'),
          ('scratch-disk-size-gb',
           ('scratchDisks.diskGb', 'ephemeralDisks.diskGb')),
          ('max-pds', 'maximumPersistentDisks'),
          ('max-total-pd-size-gb', 'maximumPersistentDisksSizeGb'),
          ('deprecation', 'deprecated.state')),
      detail=(
          ('name', 'name'),
          ('description', 'description'),
          ('zone', 'zone'),
          ('creation-time', 'creationTimestamp'),
          ('cpus', 'guestCpus'),
          ('memory-mb', 'memoryMb'),
          ('scratch-disk-size-gb',
           ('scratchDisks.diskGb', 'ephemeralDisks.diskGb')),
          ('max-pds', 'maximumPersistentDisks'),
          ('max-total-pd-size-gb', 'maximumPersistentDisksSizeGb'),
          ('available-zones', 'availableZone'),
          ('deprecation', 'deprecated.state'),
          ('replacement', 'deprecated.replacement')),
      sort_by='name')

  resource_collection_name = 'machineTypes'

  def __init__(self, name, flag_values):
    super(MachineTypeCommand, self).__init__(name, flag_values)
    flags.DEFINE_string('zone',
                        None,
                        'The zone for this request.',
                        flag_values=flag_values)

  def SetApi(self, api):
    """Set the Google Compute Engine API for the command.

    Args:
      api: The Google Compute Engine API used by this command.

    Returns:
      None.

    """
    self._machine_type_api = api.machineTypes()
    self._zones_api = api.zones()

  def _PrepareRequestArgs(self, machine_type_name, **other_args):
    """Gets the dictionary of API method keyword arguments.

    Args:
      machine_type_name:  The name of the machine type.
      **other_args:  Keyword arguments that should be included in the request.

    Returns:
      Dictionary of keyword arguments that should be passed in the API call,
      includes all keyword arguments passed in 'other_args' plus common keys
      such as the name of the resource and the project.
    """
    kwargs = {
        'project': self._project,
        'machineType': self.DenormalizeResourceName(machine_type_name)
    }
    if self._IsUsingAtLeastApiVersion('v1beta15') and self._flags.zone:
      kwargs['zone'] = self._flags.zone
    for key, value in other_args.items():
      kwargs[key] = value
    return kwargs


class GetMachineType(MachineTypeCommand):
  """Get a machine type."""

  def __init__(self, name, flag_values):
    super(GetMachineType, self).__init__(name, flag_values)

  def Handle(self, machine_type_name):
    """Get the specified machine type.

    Args:
      machine_type_name: Name of the machine type to get.

    Returns:
      The result of getting the machine type.
    """
    machine_type_name = self.DenormalizeResourceName(machine_type_name)

    machine_request = self._machine_type_api.get(
        **self._PrepareRequestArgs(machine_type_name))

    return machine_request.execute()


class ListMachineTypes(MachineTypeCommand,
                       command_base.GoogleComputeListCommand):
  """List the machine types for a project."""

  def IsZoneLevelCollection(self):
    return self._IsUsingAtLeastApiVersion('v1beta15')

  def IsGlobalLevelCollection(self):
    return not self._IsUsingAtLeastApiVersion('v1beta15')

  def __init__(self, name, flag_values):
    super(ListMachineTypes, self).__init__(name, flag_values)

  def ListFunc(self):
    """Returns the function for listing machine types."""
    return self._machine_type_api.list

  def ListZoneFunc(self):
    """Returns the function for listing machine types in a zone."""
    return self._machine_type_api.list

  def ListAggregatedFunc(self):
    """Returns the function for listing machine types across all zones."""
    if self._IsUsingAtLeastApiVersion('v1beta15'):
      return self._machine_type_api.aggregatedList


def AddCommands():
  appcommands.AddCmd('getmachinetype', GetMachineType)
  appcommands.AddCmd('listmachinetypes', ListMachineTypes)
