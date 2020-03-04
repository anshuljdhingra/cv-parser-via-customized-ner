class SpacyTraining:
    test_size = 0
    n_iter = 400
    early_stopping = 50
    dropout = 0.35
    model = "en_core_web_md"


class FlaskConfig:
    UPLOAD_FOLDER = "/app/uploaded"
    MAX_CONTENT_LENGTH = 32 * 1024 * 1024
    JSONIFY_PRETTYPRINT_REGULAR = True
