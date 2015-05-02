#!/usr/bin/env python2
# Pyrtal is a lightweight file fetching proxy
# TODO:

from flask import Flask, url_for, redirect, render_template, send_from_directory, request, g, abort
import requests
import re
import gc
import os
import time
import hashlib
from urlparse import urlsplit

# fireup our flask app ;)
app = Flask(__name__)


# app config
app.config.update(dict(
    BL_HOST='djh.im',
    BL_SCHEME='https',
    BL_PORT='NULL',
    BL_QUERY='sb',
    CACHE_DIR=os.path.join(app.root_path, 'cache'),
    TMP_DIR=os.path.join(app.root_path, 'cache/tmp'),
    LOG_DIR=os.path.join(app.root_path, 'log'),
    BUFFER_SIZE=4096 * 64
))

app.config.from_envvar('PYRTAL_CFG', silent=True)

re_host = re.compile(app.config['BL_HOST'])
re_scheme = re.compile(app.config['BL_SCHEME'])
re_port = re.compile(app.config['BL_PORT'])
re_query = re.compile(app.config['BL_QUERY'])


# Let's web2.0
@app.route('/')
# TODO: if have cookie, go to offer_lie()
def entry(method=['GET', 'POST']):
    if request.method == 'GET':
        if request.args.get('fetch') is None:
            return render_template('index.html')
        else:
            g.fetchuri = request.args.get('fetch').strip()
            filter_uri()
    else:
        #TODO: Convert JSON recved bind to g
        pass
    satisfy_config()

def filter_uri():
    r = urlsplit(getattr(g, 'fetchuri'), 'http', False)
    if r.netloc is None:
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
    query = getattr(g, 'query')

    if re_host.search(host) or re_port.search(port) or re_query.search(query) or re_scheme.search(scheme):
        raise
    # OK, now I am satisfied, offer tempf to cache content
    g.downloading = 1
    g.filename = path.split('/')[-1]
    g.tempfile = os.path.join(app.config['TMP_DIR'],
            '_'.join([str(int(time.time())),
        getattr(g, 'filename')]))
    fetchuri()

def rescue_broken_uri():
    """
    Fix URI has no scheme and leading '//'
    With prefix an // and default scheme to the fetchuri
    """
    broken = getattr(g, 'fetchuri')
    g.fetchuri = '//' + broken
    filter_uri()

def fetchuri():
    # TODO: pleasure people with cookie
    with open(getattr(g, 'tempfile'), 'wb') as fd:
        # TODO: exception about connection
        # TODO: requests.exceptions.ConnectionError
        req_header = {'User-Agent': 'pyrtal/0.0.1', 'Host': getattr(g, 'host')}
        r = requests.get(getattr(g, 'scheme') + '://' + getattr(g, 'user') + ':'
                + getattr(g, 'passwd') + '@' + getattr(g, 'host') + ':' +
                getattr(g, 'port') + getattr(g, 'path') + getattr(g, 'query'),
                stream=True, headers=req_header)
        raise
        if r.status_code != requests.codes.ok:
            raise
        for block in r.iter_content(app.config['BUFFER_SIZE']):
            if not block:
                break
            fd.write(block)
            fd.flush()
            os.fsync(fd.fileno())

    gc.collect()

    # Download ends
    g.downloading = 0
    offer_lie()

def offer_lie():
    f_hash = sha256_first128b_ver3(getattr(g, 'tempfile'), hashlib.sha256())
    stat = os.stat(getattr(g, 'tempfile'))
    f_time = time.asctime(time.localtime(stat.st_mtime))
    f_size = stat.st_size
    return render_template('offer.html', size=f_size, time=f_time,
            hash=f_hash, dluri='http://z.cn', filename=getattr(g,
                'filename'), fetchuri=getattr(g, 'fetchuri'),
            dlstatus=getattr(g, 'downloading'))



def sha256_first128b_ver3(afile, hasher, blocksize=128):
        with open(afile, 'rb') as buf:
            hasher.update(buf.read(blocksize))
            return hasher.hexdigest()


# Temp area
@app.route('/dl')
def setupdlpage():
    return render_template('offer.html', size=55555,
            time=time.asctime(time.localtime()), hash=
            sha256_first128b_ver3('/etc/passwd', hashlib.sha256()),
            dluri='2', filename='yolo', fetchuri='https://we.djh.im', dlstatus=0)
    raise





@app.route('/robots.txt')
@app.route('/sitemap.xml')
def offer_robotsrule():
    return send_from_directory(app.static_folder, request.path[1:])


if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1')
