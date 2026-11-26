# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.
#
# MIT License
#
# Copyright (c) 2021-2026 SweepMe! GmbH (sweep-me.net)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# SweepMe! driver
# * Module: Logger
# * Instrument: PC CPU and Memory usage

"""SweepMe! driver that logs the CPU, memory and disk usage of the PC."""

from __future__ import annotations

import os
from typing import Annotated

import psutil
from pysweepme import EmptyDevice
from pysweepme.commands import Unit, command

Percent = Annotated[float, Unit("%")]


class Device(EmptyDevice):
    """Driver that returns the CPU, memory and disk usage of the PC and the memory usage of SweepMe!."""

    def __init__(self) -> None:
        """Define the returned variables."""
        super().__init__()

        self.variables = ["CPU usage", "Memory usage", "Disk (C:) usage", "SweepMe! memory usage"]
        self.units = ["%", "%", "%", "%"]
        self.plottype = [True, True, True, True]
        self.savetype = [True, True, True, True]

        self.sweepme_process: psutil.Process | None = None

    def initialize(self) -> None:
        """Find the process of SweepMe!, i.e. the process the driver runs in."""
        self.sweepme_process = psutil.Process(os.getpid())

    def call(self) -> list[float]:
        """Return the CPU, memory and disk usage and the memory usage of SweepMe!."""
        return [
            self.get_cpu_usage(),
            self.get_memory_usage(),
            self.get_disk_usage(),
            self.get_process_memory_usage(),
        ]

    # --- communication commands ---------------------------------------------

    @command(returns=("cpu_usage",))
    def get_cpu_usage(self) -> Percent:
        """Return the CPU usage since the previous call; the first call of a process returns 0."""
        return float(psutil.cpu_percent())

    @command(returns=("memory_usage",))
    def get_memory_usage(self) -> Percent:
        """Return the share of the physical memory of the PC that is in use."""
        return float(psutil.virtual_memory().percent)

    @command(returns=("disk_usage",))
    def get_disk_usage(self) -> Percent:
        """Return the share of drive C: that is in use."""
        return float(psutil.disk_usage("c:").percent)

    @command(returns=("process_memory_usage",))
    def get_process_memory_usage(self) -> Percent:
        """Return the share of the physical memory used by SweepMe!, i.e. the process the driver runs in."""
        if self.sweepme_process is None:
            self.sweepme_process = psutil.Process(os.getpid())
        return float(self.sweepme_process.memory_percent())
