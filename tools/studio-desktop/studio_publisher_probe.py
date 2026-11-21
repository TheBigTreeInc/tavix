"""Explicit read-only reachability checks for configured operator destinations.

No credentials, POST, writes, redirects, privileged registry methods or releases.
A reachable endpoint never proves publisher authorization or service integration.
"""
from __future__ import annotations
import re
import ssl
import urllib.error
import urllib.request
from datetime import datetime, timezone

REPO = re.compile(r'^[A-Za-z0-9._-]{1,80}/[A-Za-z0-9._-]{1,80}$')
HOST = re.compile(r'^https://[A-Za-z0-9.-]{1,172}$')

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def _probe(url: str, service: str) -> dict:
    # Disable ambient HTTP proxy and redirect forwarding. No auth headers.
    opener = urllib.request.build_opener(
        urllib.request.ProxyHandler({}), NoRedirect(),
        urllib.request.HTTPSHandler(context=ssl.create_default_context()))
    request = urllib.request.Request(url,method='HEAD',headers={'User-Agent':'TaviX-Studio-Readiness/1','Accept':'application/json'})
    try:
        with opener.open(request, timeout=4) as reply:
            status=reply.status
    except urllib.error.HTTPError as exc:
        status=exc.code
    except (OSError, TimeoutError, urllib.error.URLError, ValueError):
        return {'service':service,'status':'unreachable','code':'DESTINATION_UNREACHABLE'}
    if 200<=status<300:
        return {'service':service,'status':'responding','code':'HTTPS_RESPONSE_RECEIVED'}
    if status in (401,403):
        return {'service':service,'status':'responding','code':'AUTHENTICATION_NOT_ESTABLISHED'}
    if status==404:
        return {'service':service,'status':'unverified','code':'DESTINATION_NOT_FOUND_OR_PRIVATE'}
    if 300<=status<400:
        return {'service':service,'status':'unverified','code':'DESTINATION_REDIRECT_REJECTED'}
    return {'service':service,'status':'unverified','code':'DESTINATION_HTTP_ERROR'}


def probe(repo: str, endpoint: str) -> dict:
    if repo and not REPO.fullmatch(repo): raise ValueError('PUBLISH_DESTINATION_INVALID')
    if endpoint and (not HOST.fullmatch(endpoint) or '..' in endpoint or endpoint.endswith('.') or endpoint[8:].startswith('.')):
        raise ValueError('PUBLISH_DESTINATION_INVALID')
    checks=[]
    if repo:
        checks.append(_probe('https://api.github.com/repos/'+repo,'github'))
    else:
        checks.append({'service':'github','status':'not_configured','code':'DESTINATION_NOT_CONFIGURED'})
    if endpoint:
        checks.append(_probe(endpoint+'/','looprd'))
    else:
        checks.append({'service':'looprd','status':'not_configured','code':'DESTINATION_NOT_CONFIGURED'})
    return {'schema':'tavix.studio.publication-probe/v1',
            'checkedAt':datetime.now(timezone.utc).isoformat(),
            'readOnly':True,'authenticated':False,'publishingAvailable':False,'checks':checks}
