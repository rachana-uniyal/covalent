# Copyright 2021 Agnostiq Inc.
#
# This file is part of Covalent.
#
# Licensed under the GNU Affero General Public License 3.0 (the "License").
# A copy of the License may be obtained with this software package or at
#
#      https://www.gnu.org/licenses/agpl-3.0.en.html
#
# Use of this file is prohibited except in compliance with the License. Any
# modifications or derivative works of this file must retain this copyright
# notice, and modified files must contain a notice indicating that they have
# been altered from the originals.
#
# Covalent is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE. See the License for more details.
#
# Relief from the License may be granted by purchasing a commercial license.

"""Tests for Covalent local executor."""

import tempfile

import covalent as ct
from covalent._workflow.transport import TransportableObject
from covalent.executor.executor_plugins.local import LocalExecutor


def test_local_executor_passes_results_dir(mocker):
    """Test that the local executor calls the stream writing function with the results directory specified in the execution arguments."""

    with tempfile.TemporaryDirectory() as tmp_dir:

        @ct.electron
        def simple_task(x):
            print(x)
            return x

        mocked_function = mocker.patch(
            "covalent.executor.executor_plugins.local.LocalExecutor.write_streams_to_file"
        )
        le = LocalExecutor()
        le.execute(
            function=TransportableObject(simple_task),
            kwargs={"x": 1},
            execution_args={"results_dir": tmp_dir},
            dispatch_id=-1,
            node_id=0,
        )
        mocked_function.assert_called_once()
