# Copyright 2013 Google Inc. All Rights Reserved.
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

"""Commands for interacting with Google Compute Engine routes."""



from google.apputils import appcommands
import gflags as flags

from gcutil import command_base


FLAGS = flags.FLAGS


class RouteCommand(command_base.GoogleComputeCommand):
  """Base command for working with the routes collection."""

  print_spec = command_base.ResourcePrintSpec(
      summary=(
          ('name', 'name'),
          ('network', 'network'),
          ('tags', 'tags'),
          ('destination-range', 'destRange'),
          ('next-hop-instance', 'nextHopInstance'),
          ('next-hop-ip', 'nextHopIp'),
          ('next-hop-gateway', 'nextHopGateway'),
          ('next-hop-network', 'nextHopNetwork'),
          ('priority', 'priority'),
          ('warning', 'warnings.code')),
      detail=(
          ('name', 'name'),
          ('description', 'description'),
          ('creation-time', 'creationTimestamp'),
          ('network', 'network'),
          ('tags', 'tags'),
          ('destination-range', 'destRange'),
          ('next-hop-instance', 'nextHopInstance'),
          ('next-hop-ip', 'nextHopIp'),
          ('next-hop-gateway', 'nextHopGateway'),
          ('next-hop-network', 'nextHopNetwork'),
          ('priority', 'priority'),
          ('warning', 'warnings.code'),
          ('warning-message', 'warnings.message')),
      sort_by='name')

  resource_collection_name = 'routes'

  def __init__(self, name, flag_values):
    super(RouteCommand, self).__init__(name, flag_values)

  def SetApi(self, api):
    """Set the Google Compute Engine API for the command.

    Args:
      api: The Google Compute Engine API used by this command.
    """
    self._routes_api = api.routes()


class AddRoute(RouteCommand):
  """Create a new entry in the project's routes collection.

  A route is a rule that specifies how matching packets should be handled by a
  virtual network.
  """
  positional_args = '<route-name>'

  def __init__(self, name, flag_values):
    super(AddRoute, self).__init__(name, flag_values)
    flags.DEFINE_string(
        'description',
        None,
        'Route description.',
        flag_values=flag_values)
    flags.DEFINE_string(
        'network',
        'default',
        'Which network to apply the route to.',
        flag_values=flag_values)
    flags.DEFINE_list(
        'tags',
        [],
        'The set of tagged instances to which the route will apply (comma '
        'separated).',
        flag_values=flag_values)
    flags.DEFINE_integer(
        'priority',
        1000,
        'Priority of this route relative to others of the same specificity.',
        lower_bound=0,
        upper_bound=2 ** 32 - 1,
        flag_values=flag_values)
    flags.DEFINE_string(
        'next_hop_instance',
        None,
        'An instance that should handle matching packets.',
        flag_values=flag_values)
    flags.DEFINE_string(
        'next_hop_ip',
        None,
        'The IP address of an instance that should handle matching packets.',
        flag_values=flag_values)
    flags.DEFINE_string(
        'next_hop_gateway',
        None,
        'The gateway that should handle matching packets.',
        flag_values=flag_values)

  def Handle(self, route_name, dest_range):
    """Add the specified route.

    Args:
      route_name: The name of the route to add.
      dest_range: Specifies which packets will be routed by destination
                  address.

    Returns:
      The result of inserting the route.

    Raises:
      command_base.CommandError: If the passed flag values cannot be
          interpreted.
    """
    route_resource = {
        'kind': self._GetResourceApiKind('route'),
        'name': self.DenormalizeResourceName(route_name),
        'description': self._flags.description,
        'destRange': dest_range,
        'tags': self._flags.tags,
        'priority': self._flags.priority,
        }

    if self._flags.network:
      route_resource['network'] = self.NormalizeGlobalResourceName(
          self._project,
          'networks',
          self._flags.network)

    if self._flags.next_hop_instance:
      route_resource['nextHopInstance'] = self.NormalizeGlobalResourceName(
          self._project,
          'instances',
          self._flags.next_hop_instance)
      if route_resource['nextHopInstance'] != self._flags.next_hop_instance:
        raise command_base.CommandError(
            self._flags['next_hop_instance'].name + ' must be an absolute URL.')

    if self._flags.next_hop_ip:
      route_resource['nextHopIp'] = self._flags.next_hop_ip
    if self._flags.next_hop_gateway:
      route_resource['nextHopGateway'] = self.NormalizeGlobalResourceName(
          self._project,
          'gateways',
          self._flags.next_hop_gateway)

    route_request = self._routes_api.insert(project=self._project,
                                            body=route_resource)
    return route_request.execute()


class GetRoute(RouteCommand):
  """Get a route."""

  positional_args = '<route-name>'

  def __init__(self, name, flag_values):
    super(GetRoute, self).__init__(name, flag_values)

  def Handle(self, route_name):
    """Get the specified route.

    Args:
      route_name: The name of the route to get.

    Returns:
      The result of getting the route.
    """
    route_request = self._routes_api.get(
        project=self._project,
        route=self.DenormalizeResourceName(route_name))
    return route_request.execute()


class DeleteRoute(RouteCommand):
  """Delete one or more objects from the routes collection.

  If multiple route names are specified, the routes will be deleted in
  parallel.
  """

  positional_args = '<route-name-1> ... <route-name-n>'
  safety_prompt = 'Delete route'

  def __init__(self, name, flag_values):
    super(DeleteRoute, self).__init__(name, flag_values)

  def Handle(self, *route_names):
    """Delete the specified route.

    Args:
      *route_names: The names of the routes to delete.

    Returns:
      Tuple (results, exceptions) - results of deleting the routes.
    """
    requests = []
    for name in route_names:
      requests.append(self._routes_api.delete(
          project=self._project,
          route=self.DenormalizeResourceName(name)))
    results, exceptions = self.ExecuteRequests(requests)
    return self.MakeListResult(results, 'operationList'), exceptions


class ListRoutes(RouteCommand, command_base.GoogleComputeListCommand):
  """List the routes collection for a project."""

  def ListFunc(self):
    """Returns the function for listing routes."""
    return self._routes_api.list


def AddCommands():
  appcommands.AddCmd('addroute', AddRoute)
  appcommands.AddCmd('getroute', GetRoute)
  appcommands.AddCmd('deleteroute', DeleteRoute)
  appcommands.AddCmd('listroutes', ListRoutes)
