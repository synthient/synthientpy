#!/usr/bin/env python
"""Tests for `synthientpy` package."""

import asyncio

# pylint: disable=redefined-outer-name
import os

from dotenv import load_dotenv

import synthientpy as synthient

load_dotenv()


# https://stackoverflow.com/questions/23033939/how-to-test-python-3-4-asyncio-code
def async_test(coro):
    def wrapper(*args, **kwargs):
        loop = asyncio.new_event_loop()
        try:
            return loop.run_until_complete(coro(*args, **kwargs))
        finally:
            loop.close()

    return wrapper


def test_sync_lookup_ip():
    client = synthient.Client(
        api_key=os.getenv("SYNTHIENT_API_KEY"),
    )
    response = client.lookup_ip("8.8.8.8")
    assert response.ip == "8.8.8.8"


@async_test
async def test_async_lookup_ip():
    client = synthient.AsyncClient(
        api_key=os.getenv("SYNTHIENT_API_KEY"),
    )
    response = await client.lookup_ip("8.8.8.8")
    assert response.ip == "8.8.8.8"


def test_sync_404():
    client = synthient.Client(
        api_key=os.getenv("SYNTHIENT_API_KEY"),
    )
    try:
        client.lookup_ip("not_an_ip")
    except (synthient.ErrorResponse, synthient.InternalServerError):
        pass


@async_test
async def test_async_404():
    client = synthient.AsyncClient(
        api_key=os.getenv("SYNTHIENT_API_KEY"),
    )
    try:
        await client.lookup_ip("not_an_ip")
    except (synthient.ErrorResponse, synthient.InternalServerError):
        pass


def test_sync_401():
    client = synthient.Client(
        api_key="INVALID_API_KEY",
    )
    try:
        client.lookup_ip("8.8.8.8")
    except synthient.ErrorResponse as e:
        assert e.message == "Invalid API key"


@async_test
async def test_async_401():
    client = synthient.AsyncClient(
        api_key="INVALID_API_KEY",
    )
    try:
        await client.lookup_ip("8.8.8.8")
    except synthient.ErrorResponse as e:
        assert e.message == "Invalid API key"


def test_sync_credits():
    client = synthient.Client(
        api_key=os.getenv("SYNTHIENT_API_KEY"),
    )
    response = client.credits()
    assert isinstance(response, dict)


@async_test
async def test_async_credits():
    client = synthient.AsyncClient(
        api_key=os.getenv("SYNTHIENT_API_KEY"),
    )
    response = await client.credits()
    assert isinstance(response, dict)
