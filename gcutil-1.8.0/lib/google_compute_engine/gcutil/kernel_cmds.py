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

"""Commands for interacting with Google Compute Engine installed kernels."""




from google.apputils import appcommands
import gflags as flags

from gcutil import command_base


FLAGS = flags.FLAGS



def RegisterCommonKernelFlags(flag_values):
  """Register common flag values for kernels."""
  flags.DEFINE_boolean('old_kernels',
                       False,
                       'List all versions of kernels',
                       flag_values=flag_values)


class KernelCommand(command_base.GoogleComputeCommand):
  """Base command for working with the kernels collection."""

  print_spec = command_base.ResourcePrintSpec(
      summary=(
          ('name', 'selfLink'),
          ('description', 'description'),
          ('deprecation', 'deprecated.state')),
      detail=(
          ('name', 'name'),
          ('description', 'description'),
          ('creation-time', 'creationTimestamp'),
          ('deprecation', 'deprecated.state'),
          ('replacement', 'deprecated.replacement')),
      sort_by='name')

  resource_collection_name = 'kernels'

  def __init__(self, name, flag_values):
    super(KernelCommand, self).__init__(name, flag_values)

  def SetApi(self, api):
    """Set the Google Compute Engine API for the command.

    Args:
      api: The Google Compute Engine API used by this command.

    Returns:
      None.

    """
    self._kernels_api = api.kernels()


class GetKernel(KernelCommand):
  """Get a kernel."""

  def __init__(self, name, flag_values):
    super(GetKernel, self).__init__(name, flag_values)

  def Handle(self, kernel_name):
    """Get the specified kernel.

    Args:
      kernel_name: The name of the kernel to get.

    Returns:
      The result of getting the kernel.
    """
    kernel_request = self._kernels_api.get(
        project=self._project,
        kernel=self.DenormalizeResourceName(kernel_name))

    return kernel_request.execute()


class ListKernels(KernelCommand, command_base.GoogleComputeListCommand):
  """List the kernels for a project."""

  def __init__(self, name, flag_values):
    super(ListKernels, self).__init__(name, flag_values)
    RegisterCommonKernelFlags(flag_values)

  def FilterResults(self, results):
    results['items'] = command_base.NewestKernelsFilter(
        self._flags, results['items'])
    return results

  def GetProjects(self):
    projects = super(ListKernels, self).GetProjects()
    projects += command_base.STANDARD_KERNEL_PROJECTS
    return list(set(projects))

  def ListFunc(self):
    """Returns the fuction for listing kernels."""
    return self._kernels_api.list


def AddCommands():
  appcommands.AddCmd('getkernel', GetKernel)
  appcommands.AddCmd('listkernels', ListKernels)
