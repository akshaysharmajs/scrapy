import unittest
from warnings import catch_warnings

import pytest

from scrapy.http import (
    Headers,
    HtmlResponse,
    Response,
    TextResponse,
    XmlResponse,
)
from scrapy.responsetypes import responsetypes, ResponseTypes
from .test_utils_response import (
    POST_XTRACTMIME_SCENARIOS,
    PRE_XTRACTMIME_SCENARIOS,
)


@pytest.mark.parametrize(
    "kwargs,response_class",
    (
        *PRE_XTRACTMIME_SCENARIOS,
        *(
            pytest.param(
                kwargs,
                response_class,
                marks=pytest.mark.xfail(
                    strict=True,
                    reason=(
                        "Expected failure of deprecated "
                        "scrapy.responsetypes.responsetypes.from_args, works "
                        "with its replacement "
                        "scrapy.utils.response.get_response_class"
                    ),
                ),
            )
            for kwargs, response_class in POST_XTRACTMIME_SCENARIOS
        ),
    ),
)
def test_from_args(kwargs, response_class):
    assert responsetypes.from_args(**kwargs) == response_class


class ResponseTypesTest(unittest.TestCase):

    def test_from_filename(self):
        mappings = [
            ('data.bin', Response),
            ('file.txt', TextResponse),
            ('file.xml.gz', Response),
            ('file.xml', XmlResponse),
            ('file.html', HtmlResponse),
            ('file.unknownext', Response),
        ]
        for source, cls in mappings:
            retcls = responsetypes.from_filename(source)
            assert retcls is cls, f"{source} ==> {retcls} != {cls}"

    def test_from_content_disposition(self):
        mappings = [
            (b'attachment; filename="data.xml"', XmlResponse),
            (b'attachment; filename=data.xml', XmlResponse),
            ('attachment;filename=data£.tar.gz'.encode('utf-8'), Response),
            ('attachment;filename=dataµ.tar.gz'.encode('latin-1'), Response),
            ('attachment;filename=data高.doc'.encode('gbk'), Response),
            ('attachment;filename=دورهdata.html'.encode('cp720'), HtmlResponse),
            ('attachment;filename=日本語版Wikipedia.xml'.encode('iso2022_jp'), XmlResponse),

        ]
        for source, cls in mappings:
            retcls = responsetypes.from_content_disposition(source)
            assert retcls is cls, f"{source} ==> {retcls} != {cls}"

    def test_from_content_type(self):
        mappings = [
            ('text/html; charset=UTF-8', HtmlResponse),
            ('text/xml; charset=UTF-8', XmlResponse),
            ('application/xhtml+xml; charset=UTF-8', HtmlResponse),
            ('application/vnd.wap.xhtml+xml; charset=utf-8', HtmlResponse),
            ('application/xml; charset=UTF-8', XmlResponse),
            ('application/octet-stream', Response),
            ('application/x-json; encoding=UTF8;charset=UTF-8', TextResponse),
            ('application/json-amazonui-streaming;charset=UTF-8', TextResponse),
        ]
        for source, cls in mappings:
            retcls = responsetypes.from_content_type(source)
            assert retcls is cls, f"{source} ==> {retcls} != {cls}"

    def test_from_body(self):
        mappings = [
            (b'\x03\x02\xdf\xdd\x23', Response),
            (b'Some plain text\ndata with tabs\t and null bytes\0', TextResponse),
            (b'<html><head><title>Hello</title></head>', HtmlResponse),
            # https://codersblock.com/blog/the-smallest-valid-html5-page/
            (b'<!DOCTYPE html>\n<title>.</title>', HtmlResponse),
            (b'<?xml version="1.0" encoding="utf-8"', XmlResponse),
        ]
        for source, cls in mappings:
            retcls = responsetypes.from_body(source)
            assert retcls is cls, f"{source} ==> {retcls} != {cls}"

    def test_from_headers(self):
        mappings = [
            ({'Content-Type': ['text/html; charset=utf-8']}, HtmlResponse),
            ({'Content-Type': ['text/html; charset=utf-8'], 'Content-Encoding': ['gzip']}, Response),
            ({'Content-Type': ['application/octet-stream'],
              'Content-Disposition': ['attachment; filename=data.txt']}, TextResponse),
        ]
        for source, cls in mappings:
            source = Headers(source)
            retcls = responsetypes.from_headers(source)
            assert retcls is cls, f"{source} ==> {retcls} != {cls}"

    def test_custom_mime_types_loaded(self):
        # check that mime.types files shipped with scrapy are loaded
        self.assertEqual(responsetypes.mimetypes.guess_type('x.scrapytest')[0], 'x-scrapy/test')


if __name__ == "__main__":
    unittest.main()
