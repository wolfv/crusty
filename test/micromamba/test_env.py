import os
import platform
import shutil
from pathlib import Path

import pytest

from .helpers import *

class TestEnv:

    current_root_prefix = os.environ["MAMBA_ROOT_PREFIX"]
    current_prefix = os.environ["CONDA_PREFIX"]
    cache = os.path.join(current_root_prefix, "pkgs")

    env_name_1 = random_string()
    env_name_2 = random_string()
    env_name_3 = random_string()
    root_prefix = os.path.expanduser(os.path.join("~", "tmproot" + random_string()))
    env_txt = Path("~/.conda/environments.txt").expanduser()
    env_txt_bkup = Path("~/.conda/environments.txt.bkup").expanduser()

    @classmethod
    def setup_class(cls):
        os.environ["MAMBA_ROOT_PREFIX"] = cls.root_prefix
        os.environ["CONDA_PREFIX"] = cls.root_prefix

        # speed-up the tests
        os.environ["CONDA_PKGS_DIRS"] = cls.cache

        if cls.env_txt.exists():
            cls.env_txt.rename(cls.env_txt_bkup)

        res = create(
            f"",
            "-n",
            cls.env_name_1,
            "--json",
            no_dry_run=True,
        )

    @classmethod
    def setup(cls):
        pass

    @classmethod
    def teardown_class(cls):
        os.environ["MAMBA_ROOT_PREFIX"] = cls.current_root_prefix
        os.environ["CONDA_PREFIX"] = cls.current_prefix
        os.environ.pop("CONDA_PKGS_DIRS")
        shutil.rmtree(cls.root_prefix)

        if cls.env_txt_bkup.exists():
            cls.env_txt_bkup.rename(cls.env_txt)

    def test_env_list(self):
        env_json = run_env("list", "--json")

        assert ("envs" in env_json)
        assert (len(env_json["envs"]) == 2)
        assert (self.root_prefix == env_json["envs"][0])
        assert (self.env_name_1 in env_json["envs"][1])

    def test_env_list_table(self):
        res = run_env("list")

        assert ("Name" in res)
        assert ("base" in res)
        assert (self.root_prefix in res)
        lines = res.splitlines()
        for l in lines:
            if "*" in l:
                active_env_l = l
        assert (self.root_prefix in active_env_l)

        full_env = self.root_prefix + "/envs/" + self.env_name_1
        os.environ["CONDA_PREFIX"] = full_env

        res = run_env("list")

        lines = res.splitlines()
        for l in lines:
            if "*" in l:
                active_env_l = l
        assert (full_env in active_env_l)

        os.environ["CONDA_PREFIX"] = self.root_prefix
