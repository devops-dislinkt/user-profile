from user_profile_service import flask_app
from user_profile_service.services.consumer_service import ConsumerThread


if __name__ == '__main__':
    consumer_t = ConsumerThread()
    consumer_t.start()
    flask_app.run(debug=True, host="0.0.0.0")