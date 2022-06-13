from user_profile_service import create_app, create_kafka_thread


if __name__ == "__main__":
    app = create_app()
    # create_kafka_thread(app)
    app.run(debug=True, host="0.0.0.0")
