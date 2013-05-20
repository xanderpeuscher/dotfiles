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

"""Commands for interacting with Google Compute Engine availability regions."""



from google.apputils import appcommands
import gflags as flags

from gcutil import command_base


FLAGS = flags.FLAGS


class RegionCommand(command_base.GoogleComputeCommand):
  """Base command for working with the regions collection."""

  print_spec = command_base.ResourcePrintSpec(
      summary=(
          ('name', 'name'),
          ('description', 'description'),
          ('status', 'status'),
          ('deprecation', 'deprecated.state')),
      detail=(
          ('name', 'name'),
          ('description', 'description'),
          ('creation-time', 'creationTimestamp'),
          ('status', 'status'),
          ('zones', 'zones'),
          ('deprecation', 'deprecated.state'),
          ('replacement', 'deprecated.replacement')),
      sort_by='name')

  def SetApi(self, api):
    """Set the Google Compute Engine API for the command.

    Args:
      api: The Google Compute Engine API used by this command.

    Returns:
      None.
    """
    self._regions_api = api.regions()


class GetRegion(RegionCommand):
  """Get a region."""

  positional_args = '<region-name>'

  def CustomizePrintResult(self, result, table):
    """Customized result printing for this type.

    Args:
      result: json dictionary returned by the server
      table: the pretty printing table to be customized

    Returns:
      None.

    """
    # Add the region quotas
    table.AddRow(('', ''))
    table.AddRow(('usage', ''))
    for quota in result.get('quotas', []):
      table.AddRow(('  %s' % quota['metric'].lower().replace('_', '-'),
                    '%s/%s' % (str(quota['usage']), str(quota['limit']))))

  def Handle(self, region_name):
    """Get the specified region.

    Args:
      region_name: Path of the region to get.

    Returns:
      The result of getting the region.
    """
    request = self._regions_api.get(project=self._project, region=region_name)
    return request.execute()


class ListRegions(RegionCommand, command_base.GoogleComputeListCommand):
  """List available regions for a project."""

  def ListFunc(self):
    return self._regions_api.list


def AddCommands():
  appcommands.AddCmd('getregion', GetRegion)
  appcommands.AddCmd('listregions', ListRegions)
