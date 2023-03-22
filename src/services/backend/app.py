"""
    The backend endpoints of our web application for the service A (Alice)
"""
import io
import os
import pandas as pd
import requests
from flask import Flask, request, json
from connector import HDFSConnector
from settings import HOST, PORT, ENVIRONMENT_DEBUG, URL_ALICE, URL_BOB
from packages.spark_commands import ThesisSparkClass
from flask_cors import CORS, cross_origin

app = Flask(__name__)
CORS(app)


@app.route('/', methods=['GET'])
def home():
    response = app.response_class(
        status=200
    )
    return response


@app.route("/start", methods=["POST"])
@cross_origin()
def start():
    response = request.get_json()

    project_name = response.get('project_name')
    cluster_a_file = response.get('file_a').get('name')
    cluster_b_file = response.get('file_b').get('name')

    if project_name is None or cluster_a_file is None or cluster_b_file is None:
        return app.response_class(
            response=json.dumps({"message": 'Files or Project name are not defined.'}),
            status=400,
        )

    response = requests.get(url=f"http://snf-34396.ok-kno.grnetcloud.net:9500/take-file/pretransformed_data?file={cluster_a_file}")
    pd.read_csv(io.StringIO(response.content.decode('utf-8'))).to_csv(f'/opt/workspace/pretransformed_data/alice_{cluster_a_file}')

    response = requests.get(url=f"http://snf-34397.ok-kno.grnetcloud.net:9500/take-file/pretransformed_data?file={cluster_b_file}")
    pd.read_csv(io.StringIO(response.content.decode('utf-8'))).to_csv(f'/opt/workspace/pretransformed_data/bob_{cluster_b_file}')

    app.logger.info(f"Downloaded")

    try:
        spark = ThesisSparkClass(project_name=project_name,
                                 file_a=cluster_a_file,
                                 file_b=cluster_b_file,
                                 logger=app)
        spark.start_etl()


    except Exception as e:
        app.logger.info(f"ERROR : {e}")
        return app.response_class(
            status=500,
            response=json.dumps({"message": f"There was an unexpected error! {e}"})
        )

    return app.response_class(
        response=json.dumps({"message": 'The join operation has finished.'}),
        status=200,
        mimetype='application/json'
    )


if __name__ == '__main__':
    app.config['SECRET_KEY'] = 'super secret key'
    app.config['SESSION_TYPE'] = 'filesystem'

    app.run(host=HOST, port=PORT, debug=ENVIRONMENT_DEBUG)
