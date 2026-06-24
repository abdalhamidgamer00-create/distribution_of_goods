"""Tests for shared.utility.archiver.zip_ops module."""

import os
import tempfile
import shutil
import zipfile

import pytest

from src.shared.utility.archiver.zip_ops import (
    write_zip_files,
    create_zip_archive,
)


@pytest.fixture
def tmp_dir():
    d = tempfile.mkdtemp()
    yield d
    shutil.rmtree(d, ignore_errors=True)


class TestWriteZipFiles:
    def test_creates_valid_zip(self, tmp_dir):
        archive_dir = os.path.join(tmp_dir, "archive")
        os.makedirs(archive_dir)
        with open(os.path.join(archive_dir, "file1.txt"), 'w') as f:
            f.write("content1")
        with open(os.path.join(archive_dir, "file2.txt"), 'w') as f:
            f.write("content2")

        zip_path = os.path.join(tmp_dir, "output.zip")
        write_zip_files(archive_dir, zip_path)

        assert os.path.exists(zip_path)
        with zipfile.ZipFile(zip_path, 'r') as zf:
            assert len(zf.namelist()) == 2

    def test_preserves_relative_paths(self, tmp_dir):
        archive_dir = os.path.join(tmp_dir, "archive")
        subdir = os.path.join(archive_dir, "sub")
        os.makedirs(subdir)
        with open(os.path.join(subdir, "nested.txt"), 'w') as f:
            f.write("nested content")

        zip_path = os.path.join(tmp_dir, "output.zip")
        write_zip_files(archive_dir, zip_path)

        with zipfile.ZipFile(zip_path, 'r') as zf:
            names = zf.namelist()
            assert any("sub" in n and "nested.txt" in n for n in names)


class TestCreateZipArchive:
    def test_creates_zip_with_default_path(self, tmp_dir):
        archive_dir = os.path.join(tmp_dir, "archive")
        os.makedirs(archive_dir)
        with open(os.path.join(archive_dir, "file.txt"), 'w') as f:
            f.write("data")

        result = create_zip_archive(archive_dir)
        assert result == f"{archive_dir}.zip"
        assert os.path.exists(result)

    def test_creates_zip_with_custom_path(self, tmp_dir):
        archive_dir = os.path.join(tmp_dir, "archive")
        os.makedirs(archive_dir)
        with open(os.path.join(archive_dir, "file.txt"), 'w') as f:
            f.write("data")

        custom_path = os.path.join(tmp_dir, "custom.zip")
        result = create_zip_archive(archive_dir, custom_path)
        assert result == custom_path
        assert os.path.exists(custom_path)

    def test_raises_for_nonexistent_directory(self):
        with pytest.raises(ValueError, match="Archive directory not found"):
            create_zip_archive("/nonexistent/archive/dir")

    def test_zip_content_is_valid(self, tmp_dir):
        archive_dir = os.path.join(tmp_dir, "archive")
        os.makedirs(archive_dir)
        with open(os.path.join(archive_dir, "test.txt"), 'w') as f:
            f.write("hello world")

        zip_path = create_zip_archive(archive_dir)
        with zipfile.ZipFile(zip_path, 'r') as zf:
            assert "test.txt" in zf.namelist()
            assert zf.read("test.txt").decode() == "hello world"
