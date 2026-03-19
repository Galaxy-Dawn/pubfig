"""Tests for public API exports."""

import importlib

import pytest

import pubfig as pf


def test_surface_is_no_longer_exported() -> None:
    assert not hasattr(pf, "surface")


def test_surface_module_is_removed() -> None:
    with pytest.raises(ModuleNotFoundError):
        importlib.import_module("pubfig.plots.surface")


def test_scatter3d_is_no_longer_exported() -> None:
    assert not hasattr(pf, "scatter3d")


def test_scatter3d_module_is_removed() -> None:
    with pytest.raises(ModuleNotFoundError):
        importlib.import_module("pubfig.plots.scatter3d")


def test_raincloud_is_exported() -> None:
    assert hasattr(pf, "raincloud")
