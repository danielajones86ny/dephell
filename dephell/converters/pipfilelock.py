# built-in
import json
from collections import OrderedDict
from hashlib import sha256

# app
from ..models import RootDependency
# from .base import BaseConverter
from .pipfile import PIPFileConverter


# https://stackoverflow.com/a/23820416
# https://github.com/pypa/pipfile/blob/master/examples/Pipfile.lock
# https://github.com/pypa/pipfile/blob/master/pipfile/api.py


class PIPFileLockConverter(PIPFileConverter):
    lock = True

    def loads(self, content) -> RootDependency:
        doc = json.loads(content, object_pairs_hook=OrderedDict)
        deps = []
        root = RootDependency(raw_name=self._get_name(content=content))
        for name, content in doc['default'].items():
            deps.extend(self._make_deps(root, name, content))
        root.attach_dependencies(deps)
        return root

    def dumps(self, reqs, project: RootDependency, content=None) -> str:
        packages = OrderedDict()
        for req in reqs:
            packages[req.name] = dict(self._format_req(req=req))

        data = OrderedDict([
            ('_meta', OrderedDict([
                ('sources', [OrderedDict([
                    ('url', 'https://pypi.python.org/simple'),
                    ('verify_ssl', True),
                    ('name', 'pypi'),
                ])]),
                ('requires', {'python_version': '2.7'}),
            ])),
            ('default', packages),
            ('develop', OrderedDict()),
        ])
        data['_meta']['hash'] = {'sha256': self._get_hash(data)}
        data['_meta']['pipfile-spec'] = 6
        return json.dumps(data, indent=4, separators=(',', ': '))

    @staticmethod
    def _get_hash(data: dict) -> str:
        content = json.dumps(data, sort_keys=True, separators=(',', ':'))
        return sha256(content.encode('utf8')).hexdigest()

    def _format_req(self, req):
        result = dict()
        for name, value in req:
            if name == 'rev':
                name = 'ref'
            if name in self.fields:
                result[name] = value
        return result