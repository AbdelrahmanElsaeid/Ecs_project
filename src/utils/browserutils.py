# import logging
# import traceback

# import httpagentparser
# from django.conf import settings

# __all__ = ['UA']

# BROWSER_SUPPORT_OK = 1
# BROWSER_SUPPORT_NO = 2
# BROWSER_SUPPORT_CRAWLER = 3

# logger = logging.getLogger(__name__)
# logger.setLevel(logging.DEBUG if settings.DEBUG else logging.INFO)
# class Version(tuple):
#     def __new__(cls, version_str):
#         version = []
#         if version_str:
#             for bit in version_str.split('.'):
#                 try:
#                     bit = int(bit)
#                 except ValueError:
#                     pass
#                 version.append(bit)
#         else:
#             version = [0,]
#         instance = super().__new__(cls, version)
#         return instance

# def parse_ua(ua_str):
#     ua = httpagentparser.detect(ua_str)
#     for x in ('browser', 'platform', 'flavor'):
#         if x in ua and 'version' in ua[x]:
#             ua[x]['version'] = tuple(map(int, ua[x]['version'].split('.')))
#     return ua


# def supported_starting(name, version):
#     version = tuple(map(int, version.split('.')))

#     def _fn(ua):
#         ua = parse_ua(ua)
#         if 'browser' in ua and 'name' in ua['browser'] and 'version' in ua['browser']:
#             b = ua['browser']
#             if b['name'] == name:
#                 if b['version'] >= version:
#                     return BROWSER_SUPPORT_OK
#                 else:
#                     return BROWSER_SUPPORT_NO

#     return _fn


# def android_quirks(ua):
#     ua = parse_ua(ua)
#     if 'browser' in ua and 'platform' in ua:
#         b = ua['browser']
#         if b.get('name', None) == 'AndroidBrowser':
#             platform = ua['platform']
#             if platform.get('name', None) == 'Android' and \
#                     platform.get('version', ()) >= (3, 2):
#                 return BROWSER_SUPPORT_OK


# def crawler_detected(ua):
#     ua = parse_ua(ua)
#     if ua.get('bot', False):
#         return BROWSER_SUPPORT_CRAWLER


# def crawler_quirks(ua_str):
#     ua_str = ua_str.lower()
#     bots = ('yahoo! slurp', 'msnbot', 'hetzner system monitoring')

#     if any(bot in ua_str for bot in bots):
#         return BROWSER_SUPPORT_CRAWLER


# # browser filtering rules; order is significant
# BROWSER_FILTER_RULES = (
#     supported_starting('Firefox', '28'),
#     supported_starting('Chrome', '29'),
#     android_quirks,
#     supported_starting('Safari', '7'),
#     supported_starting('Microsoft Internet Explorer', '11'),
#     supported_starting('MSEdge', '12.10240'),  # Edge 20 (first public release)
#     crawler_detected,
#     crawler_quirks,
# )


# class UA(object):
#     def __init__(self, ua_str):
#         self.support = None
#         for rule_fn in BROWSER_FILTER_RULES:
#             try:
#                 support = rule_fn(ua_str)
#                 if support is not None:
#                     self.support = support
#                     break
#             except Exception as e:
#                 logger.info('UA string parsing threw an exception\nUA string: %s\n%s', ua_str,
#                             traceback.format_exc())

#     @property
#     def is_supported(self):
#         return self.support == BROWSER_SUPPORT_OK

#     @property
#     def is_unsupported(self):
#         return self.support == BROWSER_SUPPORT_NO

#     @property
#     def is_crawler(self):
#         return self.support == BROWSER_SUPPORT_CRAWLER












#------------------------------------------- Old Code----------------------------------------------


import logging, traceback

import httpagentparser
from django.conf import settings

__all__ = ['UA']

BROWSER_SUPPORT_OK = 1
BROWSER_SUPPORT_NO = 2
BROWSER_SUPPORT_CRAWLER = 3

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG if settings.DEBUG else logging.INFO)

class Version(tuple):
    def __new__(cls, version_str):
        version = []
        if version_str:
            for bit in version_str.split('.'):
                try:
                    bit = int(bit)
                except ValueError:
                    pass
                version.append(bit)
        else:
            version = [0,]
        instance = super().__new__(cls, version)
        return instance

def parse_ua(ua_str):
    ua = httpagentparser.detect(ua_str)
    for x in ('browser', 'platform', 'flavor'):
        if x in ua and 'version' in ua[x]:
            ua[x]['version'] = Version(ua[x]['version'])
    return ua

def supported_starting(name, version):
    version = Version(version)

    def _fn(ua):
        ua = parse_ua(ua)
        if 'browser' in ua and 'name' in ua['browser'] and 'version' in ua['browser']:
            b = ua['browser']
            if b['name'] == name:
                if b['version'] >= version:
                    return BROWSER_SUPPORT_OK
                else:
                    return BROWSER_SUPPORT_NO
    return _fn

def android_quirks(ua):
    ua = parse_ua(ua)
    if 'browser' in ua and 'platform' in ua:
        b = ua['browser']
        if b.get('name', None) == 'AndroidBrowser':
            platform = ua['platform']
            if platform.get('name', None) == 'Android' and \
                platform.get('version',  Version('0')) >= '3.2':
                return BROWSER_SUPPORT_OK

def crawler_detected(ua):
    ua = parse_ua(ua)
    if ua.get('bot', False):
        return BROWSER_SUPPORT_CRAWLER

def crawler_quirks(ua_str):
    ua_str = ua_str.lower()
    bots = ('yahoo! slurp', 'msnbot', 'hetzner system monitoring')

    if any(bot in ua_str for bot in bots):
        return BROWSER_SUPPORT_CRAWLER

# browser filtering rules; order is significant
BROWSER_FILTER_RULES = (
    supported_starting('Firefox', '28'),
    supported_starting('Chrome', '29'),
    android_quirks,
    supported_starting('Safari', '7'),
    supported_starting('Microsoft Internet Explorer', '11'),
    supported_starting('MSEdge', '12.10240'),   # Edge 20 (first public release)
    crawler_detected,
    crawler_quirks,
)

class UA(object):
    def __init__(self, ua_str):
        self.support = None
        for rule_fn in BROWSER_FILTER_RULES:
            try:
                support = rule_fn(ua_str)
                if not support is None:
                    self.support = support
                    break
            except Exception as e:
                logger.info('UA string parsing threw an exception\nUA string: %s\n%s', ua_str, traceback.format_exc())

    is_supported = property(lambda self: self.support == BROWSER_SUPPORT_OK)
    is_unsupported = property(lambda self: self.support == BROWSER_SUPPORT_NO)
    is_crawler = property(lambda self: self.support == BROWSER_SUPPORT_CRAWLER)
