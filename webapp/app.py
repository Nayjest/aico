import os
import sys
import json
from flask import Flask, render_template, request, send_from_directory
# add parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


import aico.bootstrap
from aico.core import *
webapp = Flask(__name__)


@webapp.route('/')
def report():
    out_folder_path = project().work_path / 'out'
    report_items = []

    for file_name in os.listdir(out_folder_path):
        if file_name.endswith('.json'):
            file_path = out_folder_path / file_name
            with open(file_path, 'r') as json_file:
                data = json.load(json_file)
                report_items += data.get('changes', [])
    return render_template('report.html', report_items=report_items)


@webapp.after_request
def add_header(response):
    if request.path.startswith('/static/'):
        response.cache_control.no_cache = True
        response.cache_control.no_store = True
        response.cache_control.must_revalidate = True
        response.headers['Pragma'] = 'no-cache'
    return response


if __name__ == '__main__':
    webapp.run(debug=False)
