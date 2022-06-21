from user_profile_service import create_app, create_kafka_thread
from flask_cors import CORS, cross_origin



if __name__ == "__main__":
    app = create_app()
    cors = CORS(app)
    app.config['CORS_HEADERS'] = 'Content-Type'
    create_kafka_thread(app)
    app.run(debug=True, host="0.0.0.0")
