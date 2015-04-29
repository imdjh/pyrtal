#!/usr/bin/env python2
# Pyrtal is a lightweight file fetching proxy
# TODO:

from flask import Flask, url_for, redirect, render_template, send_from_directory, request
import requests
import shutil
import ftplib
import importlib


# fireup our flask app ;)
app = Flask(__name__)

@app.route('/portal/<path:url>')
def portal(url):
    with urllib.request.urlopen(url) as response, open('/var/tmp/' + 'ramdom-bits', 'wb') as out_file:
        shutil.copyfileobj(response, out_file)
    return redirect('http://localhost/' + 'ramdom-bits', code=301)

@app.route('/')
def offer_index():
    return render_template('index.html')

@app.route('/robots.txt')
@app.route('/sitemap.xml')
def offer_robotsrule():
    return send_from_directory(app.static_folder, request.path[1:])

@app.route('/ftp')
def ftpportal():
    ftp = ftplib.FTP('ftp.kernel.org', 'anonymous', 'pyrtal@')
    ftp.cwd("/pub/linux/kernel")
    ftp.retrlines('RETR ' + 'README', open('/var/tmp/KREADME', 'a+').write)
    return redirect('http://localhost/getfiles/KREADME', code=301)


if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1')
