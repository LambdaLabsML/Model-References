# Copyright (c) 2021, NVIDIA CORPORATION. All rights reserved.
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
###############################################################################
# Copyright (C) 2021 Habana Labs, Ltd. an Intel Company
# All Rights Reserved.
#
# Unauthorized copying of this file or any element(s) within it, via any medium
# is strictly prohibited.
# This file contains Habana Labs, Ltd. proprietary and confidential information
# and is subject to the confidentiality and license agreements under which it
# was provided.
#
###############################################################################


import os
from argparse import ArgumentDefaultsHelpFormatter, ArgumentParser
from os.path import dirname
from subprocess import call

parser = ArgumentParser(ArgumentDefaultsHelpFormatter)
parser.add_argument("--mode", type=str, required=True, choices=["train", "predict"], help="Benchmarking mode")
parser.add_argument("--task", type=str, default="01", help="Task code")
parser.add_argument("--gpus", type=int, default=1, help="Number of GPUs to use")
parser.add_argument("--dim", type=int, required=True, help="Dimension of UNet")
parser.add_argument("--batch_size", type=int, default=2, help="Batch size")
parser.add_argument("--amp", action="store_true", help="Enable automatic mixed precision")
parser.add_argument("--train_batches", type=int, default=150, help="Number of batches for training")
parser.add_argument("--test_batches", type=int, default=150, help="Number of batches for inference")
parser.add_argument("--warmup", type=int, default=50, help="Warmup iterations before collecting statistics")
parser.add_argument("--results", type=str, default="/results", help="Path to results directory")
parser.add_argument("--logname", type=str, default="perf.json", help="Name of dlloger output")
parser.add_argument("--profile", action="store_true", help="Enable dlprof profiling")

if __name__ == "__main__":
    args = parser.parse_args()
    path_to_main = os.path.join(dirname(dirname(os.path.realpath(__file__))), "main.py")
    cmd = ""
    cmd += f"python main.py --task {args.task} --benchmark --max_epochs 2 --min_epochs 1 --optimizer adam "
    cmd += f"--results {args.results} "
    cmd += f"--logname {args.logname} "
    cmd += f"--exec_mode {args.mode} "
    cmd += f"--dim {args.dim} "
    cmd += f"--gpus {args.gpus} "
    cmd += f"--train_batches {args.train_batches} "
    cmd += f"--test_batches {args.test_batches} "
    cmd += f"--warmup {args.warmup} "
    cmd += "--amp " if args.amp else ""
    cmd += "--profile " if args.profile else ""
    if args.mode == "train":
        cmd += f"--batch_size {args.batch_size} "
    else:
        cmd += f"--val_batch_size {args.batch_size} "
    call(cmd, shell=True)
