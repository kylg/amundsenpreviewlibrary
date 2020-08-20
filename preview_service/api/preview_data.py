from http import HTTPStatus
from typing import Any, Iterable  # noqa: F401
import logging
from flask_restful import Resource, reqparse
from flasgger import swag_from
from flask import current_app
from preview_service import config
from os import path
from preview_service.models.preview_data import ColumnItem, PreviewData, PreviewDataSchema
import csv
from flask import request
from werkzeug.utils import secure_filename
import os


class PreviewDataAPI(Resource):
    """
    Preview Data API
    """

    def __init__(self) -> None:
        super(PreviewDataAPI, self).__init__()
        self.preview_file_path = current_app.config[config.PREVIEW_FILE_REPO]
        self.get_parser = reqparse.RequestParser(bundle_errors=True)
        self.get_parser.add_argument('database', required=True, type=str)
        self.get_parser.add_argument('schema', required=False, default="", type=str)
        self.get_parser.add_argument('tableName', required=True, default="", type=str)

    @swag_from('swagger_doc/preview_data_post.yml')
    def post(self) -> Iterable[Any]:
        """
        Fetch preview data based on database, schema and tableName

        :return: list of table results. List can be empty if query
        doesn't match any tables
        """
        args = self.get_parser.parse_args(strict=True)
        database = args.get('database')
        schema = args.get('schema')
        table_name = args.get('tableName')

        try:
            data_file = '{base}/{db}.{tbl}.csv'.format(base=self.preview_file_path, db=database, tbl=table_name)
            if path.exists(data_file):
                logging.info('csv {csvFile} exist for preview'.format(csvFile=data_file))
                with open(data_file, newline='') as csvfile:
                    reader = csv.DictReader(csvfile, delimiter=',')
                    cols = []
                    for f in reader.fieldnames:
                        cols.append(ColumnItem(f, "String"))
                    data = []
                    for row in reader:
                        data.append(row)
                    preview_data = PreviewData(database, schema, table_name, cols, data)
                    return PreviewDataSchema().dump(preview_data).data, HTTPStatus.OK
            else:
                logging.info('csv {csvFile} not exist'.format(csvFile=data_file))
                return '', HTTPStatus.NOT_FOUND
        except RuntimeError:
            err_msg = 'Exception encountered while processing preview request'
            return {'message': err_msg}, HTTPStatus.INTERNAL_SERVER_ERROR

    #turn off swag since flasgger doesn't support upload file
    #@swag_from('swagger_doc/preview_data_put.yml')
    def put(self):
        try:
            # check if the post request has the file part
            if 'file' not in request.files:
                return {'message': 'file parameter needed in the body'}, HTTPStatus.INTERNAL_SERVER_ERROR
            file = request.files['file']
            # if user does not select file, browser also
            # submit an empty part without filename
            if file.filename == '' or not file.filename.lower().endswith('.csv'):
                return {'message': 'invalid file'}, HTTPStatus.INTERNAL_SERVER_ERROR

            database = request.form['database']
            # dbschema = request.form['dbschema']
            tableName = request.form['tableName']
            file_name = "{database}.{tableName}.csv".format(database=database, tableName=tableName)
            if file:
                file_name = secure_filename(file_name)
                file.save(os.path.join(self.preview_file_path, file_name))
                return '', HTTPStatus.OK
        except RuntimeError:
            err_msg = 'Exception encountered while processing uploading request'
            return {'message': err_msg}, HTTPStatus.INTERNAL_SERVER_ERROR
