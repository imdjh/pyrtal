#!/usr/bin/env python2
# Pyrtal is a lightweight file fetching proxy
# TODO:

from flask import Flask, url_for, redirect, render_template, send_from_directory, request, g, abort
import requests
import re
import os
from urlparse import urlsplit
import shutil
import ftplib
import importlib

# fireup our flask app ;)
app = Flask(__name__)


# app config
app.config.update(dict(
    BL_HOST='djh.im',
    BL_SCHEME='https',
    BL_PORT='NULL',
    BL_QUERY='sb',
    CACHE_DIR=os.path.join(app.root_path, 'cache'),
    LOG_DIR=os.path.join(app.root_path, 'log')
))

app.config.from_envvar('PYRTAL_CFG', silent=True)

re_host = re.compile(app.config['BL_HOST'])
re_scheme = re.compile(app.config['BL_SCHEME'])
re_port = re.compile(app.config['BL_PORT'])
re_query = re.compile(app.config['BL_QUERY'])


# Let's web2.0
@app.route('/')
def entry(method=['GET', 'POST']):
    if request.method == 'GET':
        g.fetchuri = request.args.get('fetch')
        if g.fetchuri is None:
            return render_template('index.html')
        else:
            filter_uri()
    else:
        #TODO: Convert JSON recved bind to g
        pass
    satisfy_config()

def filter_uri():
    r = urlsplit(getattr(g, 'fetchuri'), 'http', False)
    if r.hostname is None:
        rescue_broken_uri()
    else:
        g.scheme = r.scheme
        g.host = r.netloc
        g.port = r.port or '80'
        g.path = r.path
        g.query = r.query
        g.user = r.username or ''
        g.passwd = r.password or ''



def satisfy_config():
    # read varible from g
    scheme = getattr(g, 'scheme')
    host = getattr(g, 'host')
    port = getattr(g, 'port')
    path = getattr(g, 'path')
    user = getattr(g, 'user')
    query = getattr(g, 'query')
    passwd = getattr(g, 'passwd')

    if re_host.search(host) or re_port.search(port) or re_query.search(query) or re_scheme.search(scheme):
        raise
    offer_download()

def rescue_broken_uri():
    """
    Fix URI has no scheme and leading '//'
    With prefix an // and default scheme to the fetchuri
    """
    broken = getattr(g, 'fetchuri')
    g.fetchuri = '//' + broken
    filter_uri()

def offer_download():
    # TODO
    pass


@app.route('/robots.txt')
@app.route('/sitemap.xml')
def offer_robotsrule():
    return send_from_directory(app.static_folder, request.path[1:])

# NO USE BLOW
@app.route('/ftp')
def ftpportal():
    ftp = ftplib.FTP('ftp.kernel.org', 'anonymous', 'pyrtal@')
    ftp.cwd("/pub/linux/kernel")
    ftp.retrlines('RETR ' + 'README', open('/var/tmp/KREADME', 'a+').write)
    return redirect('http://localhost/getfiles/KREADME', code=301)

@app.route('/portal/<path:url>')
def portal(url):
    with urllib.request.urlopen(url) as response, open('/var/tmp/' + 'ramdom-bits', 'wb') as out_file:
        shutil.copyfileobj(response, out_file)
    return redirect('http://localhost/' + 'ramdom-bits', code=301)

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1')
