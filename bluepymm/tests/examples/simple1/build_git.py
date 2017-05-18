import os
import shutil
import contextlib

import sh


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

    tmp_git_dir = 'tmp_git'
    git_subdir = 'subdir'
    orig_dir = '../../data/emodels_dir'

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
