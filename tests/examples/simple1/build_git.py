#!/usr/bin/env python

"""
Copyright (c) 2018, EPFL/Blue Brain Project

 This file is part of BluePyMM <https://github.com/BlueBrain/BluePyMM>

 This library is free software; you can redistribute it and/or modify it under
 the terms of the GNU Lesser General Public License version 3.0 as published
 by the Free Software Foundation.

 This library is distributed in the hope that it will be useful, but WITHOUT
 ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
 FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more
 details.

 You should have received a copy of the GNU Lesser General Public License
 along with this library; if not, write to the Free Software Foundation, Inc.,
 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
"""


import os
import shutil
import contextlib

import sh

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


@contextlib.contextmanager
def cd(dir_name):
    """Change directory"""
    old_cwd = os.getcwd()
    os.chdir(dir_name)
    try:
        yield
    finally:
        os.chdir(old_cwd)


def main():
    """Main"""

    tmp_git_dir = os.path.join(BASE_DIR, 'tmp_git')
    git_subdir = 'subdir'
    orig_dir = os.path.join(BASE_DIR, 'data/emodels_dir')

    if os.path.exists(tmp_git_dir):
        shutil.rmtree(tmp_git_dir)

    os.makedirs(tmp_git_dir)

    with cd(tmp_git_dir):
        sh.git('init')

        sh.git.config('user.name', 'dummy')
        sh.git.config('user.email', 'dummy@dummy.com')

        main_files = ['final.json', 'emodel_etype_map.json']

        os.makedirs(git_subdir)

        with cd(git_subdir):
            for filename in main_files:
                shutil.copy(os.path.join(orig_dir, git_subdir, filename), '.')
                sh.git.add(filename)

        sh.git.commit('-m', 'main')

        with cd(git_subdir):
            for emodel_n in ['1', '2']:
                sh.git.checkout('master')
                sh.git.checkout('-b', 'emodel%s' % emodel_n)
                model_files = [
                    "morphologies/morph%s.asc" % emodel_n,
                    "setup/evaluator.py",
                    "setup/__init__.py"]

                for filename in model_files:
                    model_file_dir = os.path.dirname(filename)
                    if not os.path.exists(model_file_dir):
                        os.makedirs(model_file_dir)
                    shutil.copy(
                        os.path.join(
                            orig_dir,
                            git_subdir,
                            filename),
                        model_file_dir)

                    sh.git.add(filename)
                sh.git.commit('-m', 'emodel%s' % emodel_n)


if __name__ == '__main__':
    main()
