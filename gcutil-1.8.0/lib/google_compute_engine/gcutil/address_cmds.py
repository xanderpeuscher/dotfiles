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

"""Commands for interacting with Google Compute Engine reserved addresses."""




from google.apputils import app
from google.apputils import appcommands
import gflags as flags

from gcutil import command_base
from gcutil import gcutil_logging


FLAGS = flags.FLAGS
LOGGER = gcutil_logging.LOGGER


class AddressCommand(command_base.GoogleComputeCommand):
  """Base command for working with the addresses collection."""

  print_spec = command_base.ResourcePrintSpec(
      summary=(
          ('name', 'name'),
          ('description', 'description'),
          ('region', 'region'),
          ('status', 'status'),
          ('ip', 'address'),
          ('user', 'user')),
      detail=(
          ('name', 'name'),
          ('description', 'description'),
          ('creation-time', 'creationTimestamp'),
          ('region', 'region'),
          ('status', 'status'),
          ('ip', 'address'),
          ('user', 'user')),
      sort_by='name')

  resource_collection_name = 'addresses'

  def __init__(self, name, flag_values):
    super(AddressCommand, self).__init__(name, flag_values)

    flags.DEFINE_string('region',
                        None,
                        'The region for this request.',
                        flag_values=flag_values)

  def SetApi(self, api):
    """Set the Google Compute Engine API for the command.

    Args:
      api: The Google Compute Engine API used by this command.

    Returns:
      None.

    """
    self._addresses_api = api.addresses()
    self._regions_api = api.regions()

  def _PrepareRequestArgs(self, address_name, **other_args):
    """Gets the dictionary of API method keyword arguments.

    Args:
      address_name: The name of the address.
      **other_args: Keyword arguments that should be included in the request.

    Returns:
      Dictionary of keyword arguments that should be passed in the API call,
      includes all keyword arguments passed in 'other_args' plus
      common keys such as the name of the resource and the project.
    """

    kwargs = {
        'project': self._project,
        'address': self.DenormalizeResourceName(address_name)
    }
    if self._flags.region:
      kwargs['region'] = self._flags.region
    for key, value in other_args.items():
      kwargs[key] = value
    return kwargs


class ReserveAddress(AddressCommand):
  """Reserve a new ip address."""

  positional_args = '<address-name>'

  def __init__(self, name, flag_values):
    super(ReserveAddress, self).__init__(name, flag_values)
    flags.DEFINE_string('description',
                        '',
                        'Address description.',
                        flag_values=flag_values)
    flags.DEFINE_string('source_address',
                        None,
                        'The already in-use address to promote to a reserved '
                        'address.',
                        flag_values=flag_values)
    flags.DEFINE_boolean('wait_until_complete',
                         False,
                         'Whether the program should wait until the address'
                         ' is reserved.',
                         flag_values=flag_values)

  def Handle(self, address_name):
    """Reserve the specified address.

    Args:
      address_name: The name of the address to add.

    Returns:
      The result of the reservation request.

    Raises:
      CommandError: If the command is unsupported in this API version.
      UsageError: If no address name is specified.
    """
    if not address_name:
      raise app.UsageError('Please specify an address name.')

    if not self._IsUsingAtLeastApiVersion('v1beta15'):
      raise command_base.CommandError(
          'The addresses collection is only supported in API versions >= '
          'v1beta15.')

    if not self._flags.region:
      self._flags.region = self._presenter.PromptForRegion(
          self._regions_api)['name']

    kind = self._GetResourceApiKind('address')

    kwargs = {'region': self.DenormalizeResourceName(self._flags.region)}

    address = {
        'kind': kind,
        'name': self.DenormalizeResourceName(address_name),
        'description': self._flags.description,
        }

    if self._flags.source_address is not None:
      address['address'] = self._flags.source_address

    request = self._addresses_api.insert(project=self._project,
                                         body=address, **kwargs)

    if self._flags.wait_until_complete and not self._flags.synchronous_mode:
      LOGGER.warn('wait_until_complete specified. Implying synchronous_mode.')
      self._flags.synchronous_mode = True

    return request.execute()


class GetAddress(AddressCommand):
  """Get a reserved address resource."""

  positional_args = '<address-name>'

  def __init__(self, name, flag_values):
    super(GetAddress, self).__init__(name, flag_values)

  def Handle(self, address_name):
    """Get the specified address.

    Args:
      address_name: The name of the address to get

    Returns:
      The result of getting the address.

    Raises:
      CommandError: If the command is unsupported in this API version.
      UsageError: If no address name is specified.
    """
    if not address_name:
      raise app.UsageError('Please specify an address name.')

    if not self._IsUsingAtLeastApiVersion('v1beta15'):
      raise command_base.CommandError(
          'The addresses collection is only supported in API versions >= '
          'v1beta15.')

    if not self._flags.region:
      self._flags.region = self.GetRegionForResource(self._addresses_api,
                                                     address_name)

    address_request = self._addresses_api.get(
        **self._PrepareRequestArgs(address_name))
    return address_request.execute()


class ReleaseAddress(AddressCommand):
  """Release one or more reserved address.

  If multiple address names are specified, the addresses will be released in
  parallel.
  """

  positional_args = '<address-name-1> ... <address-name-n>'
  safety_prompt = 'Release address'

  def __init__(self, name, flag_values):
    super(ReleaseAddress, self).__init__(name, flag_values)

  def Handle(self, *address_names):
    """Delete the specified addresses.

    Args:
      *address_names: The names of the addresses to release.

    Returns:
      Tuple (results, exceptions) - results of deleting the addresses.
    """
    if not self._flags.region:
      if len(address_names) > 1:
        self._flags.region = self._GetRegion()
      else:
        self._flags.region = self.GetRegionForResource(self._addresses_api,
                                                       address_names[0])
    requests = []
    for name in address_names:
      requests.append(self._addresses_api.delete(
          project=self._project,
          region=self._flags.region,
          address=self.DenormalizeResourceName(name)))
    results, exceptions = self.ExecuteRequests(requests)
    return (self.MakeListResult(results, 'operationList'), exceptions)


class ListAddresses(AddressCommand, command_base.GoogleComputeListCommand):
  """List the addresses for a project."""

  def IsZoneLevelCollection(self):
    return False

  def IsRegionLevelCollection(self):
    return True

  def IsGlobalLevelCollection(self):
    return False

  def __init__(self, name, flag_values):
    super(ListAddresses, self).__init__(name, flag_values)

  def ListFunc(self):
    """Returns the function for listing addresses."""
    return None

  def ListRegionFunc(self):
    """Returns the function for listing addresses in a region."""
    return self._addresses_api.list

  def ListAggregatedFunc(self):
    """Returns the function for listing addresses across all regions."""
    return self._addresses_api.aggregatedList


def AddCommands():
  appcommands.AddCmd('reserveaddress', ReserveAddress)
  appcommands.AddCmd('getaddress', GetAddress)
  appcommands.AddCmd('releaseaddress', ReleaseAddress)
  appcommands.AddCmd('listaddresses', ListAddresses)
