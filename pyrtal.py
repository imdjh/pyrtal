#!/usr/bin/env python2
# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8
# Pyrtal is a lightweight file fetching proxy

from flask import Flask, url_for, redirect, render_template, send_from_directory, request, g, abort, make_response
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
# TODO: if have cookie, go to offer_cake()
def entry(method=['GET', 'POST']):
    if request.method == 'GET':
        if request.args.get('fetch') is None:
            return render_template('index.html')
        elif request.cookies.get('file'):
            raise
            f_name = request.cookies.get('file')
            f_hash = getattr(g, 'hash')
            stat = os.stat(getattr(g, 'cake'))
            f_time = time.asctime(time.localtime(stat.st_mtime))
            f_size = stat.st_size
            return render_template('offer.html', size=f_size, time=f_time,
            hash=f_hash, dluri='http://127.0.0.1:5000/pray/for/' + f_hash,
            filename=f_file, fetchuri=getattr(g, 'fetchuri'),
            dlstatus=getattr(g, 'downloading'), avgspeed=getattr(g,
                'avg_speed'))
        else:
            g.fetchuri = request.args.get('fetch').strip()
            # TODO: blocked IO
            filter_uri()
            satisfy_config()

    else:
        #TODO: Convert JSON recved bind to g
        pass
    f_hash = getattr(g, 'hash')
    stat = os.stat(getattr(g, 'cake'))
    f_time = time.asctime(time.localtime(stat.st_mtime))
    f_size = stat.st_size
    # TODO: dluri try url_for
    offer_response = make_response(render_template('offer.html', size=f_size, time=f_time,
            hash=f_hash, dluri='http://127.0.0.1:5000/pray/for/' + f_hash, filename=getattr(g,
                'filename'), fetchuri=getattr(g, 'fetchuri'),
            dlstatus=getattr(g, 'downloading'), avgspeed=getattr(g,
                'avg_speed')))
    offer_response.set_cookie('file', value=getattr(g, 'filename'))
    return offer_response


def filter_uri():
    r = urlsplit(getattr(g, 'fetchuri'), 'http', False)
    if r.netloc == '':
        # Using message key send defult scheme
        g.message = r.scheme
        rescue_broken_uri()
    else:
        g.scheme = r.scheme
        g.host = r.netloc
        g.port = r.port or '80'
        g.path = r.path or '/'
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
        abort(403)
    # OK, now I am satisfied, offer tempf to cache content
    g.start_time = time.time()
    g.downloading = 1
    g.filename = path.split('/')[-1] or 'for_fool.binary'
    g.tempfile = os.path.join(app.config['TMP_DIR'],
            '_'.join([str(time.time()),
        getattr(g, 'filename')]))
    fetchuri()

def rescue_broken_uri():
    """
    Fix URI has no scheme and leading '//'
    With prefix an // with default scheme to the fetchuri
    """
    broken = getattr(g, 'fetchuri')
    g.fetchuri = getattr(g, 'message') + '://' + broken
    filter_uri()

def fetchuri():
    with open(getattr(g, 'tempfile'), 'wb') as fd:
        req_header = {'User-Agent': 'pyrtal/0.0.1', 'Host': getattr(g, 'host')}
        requests_uri = getattr(g, 'scheme') + '://' + getattr(g, 'user') + ':' + getattr(g, 'passwd') + '@' + getattr(g, 'host') + ':' + getattr(g, 'port') + getattr(g, 'path') + getattr(g, 'query')
        #flask will capture exceptions
        r = requests.get(requests_uri, stream=True, headers=req_header)

        # handle unexcept condition
        if r.status_code != requests.codes.ok:
            raise requests.exceptions.RequestException

        g.suggests_size = r.headers.get('content-length')
        if getattr(g, 'suggests_size') is None:
            fd.write(r.content)

        ix = 0
        for block in r.iter_content(app.config['BUFFER_SIZE']):
            if not block:
                break
            fd.write(block)
            ix += 1
            g.percent = int(100 * ix * app.config['BUFFER_SIZE'] /
                    int(getattr(g, 'suggests_size')))
            if getattr(g, 'percent') > 1:
                g.percent = 100
            t_stat = os.stat(getattr(g, 'tempfile'))
            fd.flush()
            os.fsync(fd.fileno())
            # FIXME: Always 0 avg speed error
            g.avg_speed = int(t_stat.st_size / (time.time() - getattr(g,
                'start_time')))

    # the download is ending...
    gc.collect()
    g.downloading = 0
    g.hash = sha256_first128b_ver3(getattr(g, 'tempfile'), hashlib.sha256())
    g.cake = os.path.join(app.config['CACHE_DIR'], getattr(g, 'hash'))
    os.rename(getattr(g, 'tempfile'), getattr(g, 'cake'))
    return 'ok'


def sha256_first128b_ver3(afile, hasher, blocksize=128):
        with open(afile, 'rb') as buf:
            hasher.update(buf.read(blocksize))
            return hasher.hexdigest()

@app.route('/pray/for/<hash>')
def offer_octostream(hash):
    # TODO: send header to corrction the filename
    return send_from_directory(app.config['CACHE_DIR'], hash)

@app.errorhandler(requests.exceptions.ConnectionError)
@app.errorhandler(requests.exceptions.RequestException)
@app.errorhandler(requests.exceptions.HTTPError)
@app.errorhandler(requests.exceptions.URLRequired)
@app.errorhandler(requests.exceptions.TooManyRedirects)
@app.errorhandler(requests.exceptions.ConnectTimeout)
@app.errorhandler(requests.exceptions.ReadTimeout)
def handle_requests_exceptions(error):

    if isinstance(error, requests.exceptions.RequestException):
        error_text = u'您的请求pyrtal开了个小差给忘了，请再试一次！ 如果多次出现，请将整个过程告诉我☞mailto://me@djh.im'
    if isinstance(error, requests.exceptions.ConnectionError):
        error_text = u'您请求的资源地址拒绝了pyrtal的请求，请和对方网站管理员联系，pyrtal对于这种情况爱莫能助'
    if isinstance(error, requests.exceptions.HTTPError):
        error_text = u'您请求的资源地址回应了一个错误的HTTP信息，对于这种情况，pyrtal爱莫能助'
    if isinstance(error, requests.exceptions.URLRequired):
        error_text = u'您输入的资源地址居然绕过了djh所预想到的所有规则，为什么给我发个邮件庆祝一下呢☞mailto://me@djh.im'
    if isinstance(error, requests.exceptions.TooManyRedirects):
        error_text = u'您请求的地址跳转了非常多次，请尝试一个更接近真正资源的地址'
    if isinstance(error, requests.exceptions.ConnectTimeout):
        error_text = u'您请求的地址在pyrtal的耐心范围内并没有应答，可能是资源服务器太忙了，也可能是资源服务器不爱pyrtal, 你应该过会儿再试试'
    if isinstance(error, requests.exceptions.ReadTimeout):
        error_text = u'您请求的服务器在pyrtal的忍受范围内没有传递哪怕一点点的数据，可能是资源服务器太忙了'
    return render_template('error.html', exceptname = error.args, rbody=error_text)




@app.route('/robots.txt')
@app.route('/sitemap.xml')
def offer_robotsrule():
    return send_from_directory(app.static_folder, request.path[1:])


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
