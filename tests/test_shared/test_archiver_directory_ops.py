"""Tests for shared.utility.archiver.directory_ops module."""

import os
import tempfile
import shutil

import pytest

from src.shared.utility.archiver.directory_ops import (
    count_directory_contents,
    prepare_archive_directory,
    copy_directory_tree,
    archive_and_copy,
)


@pytest.fixture
def tmp_dir():
    d = tempfile.mkdtemp()
    yield d
    shutil.rmtree(d, ignore_errors=True)


class TestCountDirectoryContents:
    def test_empty_directory(self, tmp_dir):
        files, dirs = count_directory_contents(tmp_dir)
        assert files == 0
        assert dirs == 0

    def test_files_only(self, tmp_dir):
        for i in range(3):
            with open(os.path.join(tmp_dir, f"file{i}.txt"), 'w') as f:
                f.write("data")
        files, dirs = count_directory_contents(tmp_dir)
        assert files == 3
        assert dirs == 0

    def test_nested_structure(self, tmp_dir):
        subdir = os.path.join(tmp_dir, "sub")
        os.makedirs(subdir)
        with open(os.path.join(subdir, "file.txt"), 'w') as f:
            f.write("data")
        files, dirs = count_directory_contents(tmp_dir)
        assert files == 1
        assert dirs == 1


class TestPrepareArchiveDirectory:
    def test_creates_archive_directories(self, tmp_dir):
        output_dir = os.path.join(tmp_dir, "output")
        archive_base = os.path.join(tmp_dir, "archive")
        os.makedirs(output_dir)
        archive_dir, archive_output = prepare_archive_directory(
            output_dir, archive_base
        )
        assert os.path.exists(archive_dir)
        assert "archive_" in os.path.basename(archive_dir)
        assert archive_output.endswith("output")

    def test_creates_base_dir_if_not_exists(self, tmp_dir):
        output_dir = os.path.join(tmp_dir, "output")
        archive_base = os.path.join(tmp_dir, "new_archive")
        os.makedirs(output_dir)
        prepare_archive_directory(output_dir, archive_base)
        assert os.path.exists(archive_base)


class TestCopyDirectoryTree:
    def test_copies_tree(self, tmp_dir):
        source = os.path.join(tmp_dir, "source")
        dest = os.path.join(tmp_dir, "dest")
        os.makedirs(source)
        with open(os.path.join(source, "file.txt"), 'w') as f:
            f.write("data")
        copy_directory_tree(source, dest)
        assert os.path.exists(os.path.join(dest, "file.txt"))

    def test_overwrites_existing_destination(self, tmp_dir):
        source = os.path.join(tmp_dir, "source")
        dest = os.path.join(tmp_dir, "dest")
        os.makedirs(source)
        os.makedirs(dest)
        with open(os.path.join(source, "new.txt"), 'w') as f:
            f.write("new")
        with open(os.path.join(dest, "old.txt"), 'w') as f:
            f.write("old")
        copy_directory_tree(source, dest)
        assert os.path.exists(os.path.join(dest, "new.txt"))
        assert not os.path.exists(os.path.join(dest, "old.txt"))


class TestArchiveAndCopy:
    def test_copies_and_returns_counts(self, tmp_dir):
        source = os.path.join(tmp_dir, "output")
        dest = os.path.join(tmp_dir, "archive_output")
        os.makedirs(source)
        with open(os.path.join(source, "file1.txt"), 'w') as f:
            f.write("data")
        with open(os.path.join(source, "file2.txt"), 'w') as f:
            f.write("data")
        files, dirs = archive_and_copy(source, dest)
        assert files == 2
        assert dirs == 0
