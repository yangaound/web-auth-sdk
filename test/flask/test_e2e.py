import pytest
from flask import Flask, jsonify

from web_auth import AuthException, Config, ConsumerInfo, ErrorCode


@pytest.fixture(scope='module')
def flask_server(jwt_payload):
    from web_auth.web_bridge.flask import FlaskBridge

    context = Config.build_context(
        web_bridge_class=FlaskBridge,
        storage_params=Config.DEFAULT_STORAGE_PARAMS,
    )

    app = Flask('test')
    app.config.update(
        {
            'TESTING': True,
        }
    )

    @app.route('/tickets')
    @context(['view_ticket'])
    def get_tickets():
        return jsonify('Hello!')

    @app.route('/delete-ticket-type', methods=['POST'])
    @context('delete_tickettype')
    def delete_ticket_type():
        return jsonify('Hello!')

    @app.route('/inject-consumer-info', methods=['POST'])
    @context([])
    def inject_consumer_info(consumer_info: ConsumerInfo):
        assert consumer_info == jwt_payload
        return jsonify('Hello!')

    @app.errorhandler(AuthException)
    def handle_exception(exception):
        response = app.make_response(({'message': str(exception), 'code': exception.code}, 403))
        return response

    yield app


@pytest.fixture()
def flask_client(flask_server):
    return flask_server.test_client()


@pytest.fixture()
def runner(flask_server):
    return flask_server.test_cli_runner()


def test_flask_app(flask_client, bearer_jwt_token):
    response = flask_client.get('/tickets', headers={'AUTHORIZATION': bearer_jwt_token})
    assert response.status_code == 200

    response = flask_client.get('/tickets', headers={})
    assert response.status_code == 403
    assert response.json['code'] == ErrorCode.UNAUTHORIZED
    assert response.json['message'] == 'Unauthorized'

    response = flask_client.post('/inject-consumer-info', headers={'AUTHORIZATION': bearer_jwt_token})
    assert response.status_code == 200

    response = flask_client.post('/inject-consumer-info')
    assert response.status_code == 403
    assert response.json['code'] == ErrorCode.UNAUTHORIZED

    response = flask_client.post('/delete-ticket-type', headers={'AUTHORIZATION': bearer_jwt_token})
    assert response.status_code == 403
    assert response.json['code'] == ErrorCode.PERMISSION_DENIED
    assert response.json['message'] == 'Permission denied'
