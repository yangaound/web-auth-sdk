import pathlib
from test._fake_web_bridge import FakeWebBridge

import pytest

from web_auth import AuthException, Config


def test_access_control():
    context = Config.build_context(
        web_bridge_class=FakeWebBridge,
    )

    reqeust = pathlib.Path('usr/etc/JWT.txt')
    context.web_bridge.access_control(reqeust, permissions={'view_order'})
    with pytest.raises(AuthException, match='Permission denied'):
        context.web_bridge.access_control(reqeust, permissions={'delete_tickettype'})
