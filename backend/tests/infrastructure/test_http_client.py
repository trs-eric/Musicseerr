from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from infrastructure.http.client import (
    HttpClientFactory,
    get_http_client,
    get_musicbrainz_http_client,
)


def _settings():
    return SimpleNamespace(
        http_timeout=10.0,
        http_connect_timeout=5.0,
        http_max_connections=200,
        http_max_keepalive=200,
        get_user_agent=lambda: "Musicseerr/test",
    )


def test_musicbrainz_uses_a_dedicated_http2_client():
    HttpClientFactory._clients.clear()

    with (
        patch("infrastructure.http.client.httpx.AsyncClient") as client_class,
        patch("infrastructure.http.client.httpx.AsyncHTTPTransport") as transport_class,
    ):
        client_class.side_effect = [MagicMock(), MagicMock()]
        default_client = get_http_client(_settings())
        musicbrainz_client = get_musicbrainz_http_client(_settings())

    assert default_client is not musicbrainz_client
    assert client_class.call_args_list[0].kwargs["http2"] is True
    assert client_class.call_args_list[1].kwargs["http2"] is True
    assert transport_class.call_args_list[0].kwargs["http2"] is True
    assert transport_class.call_args_list[1].kwargs["http2"] is True

    HttpClientFactory._clients.clear()
