# future imports
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

# stdlib imports
import os
import re
import json


def load_config(path='.env'):
    """Pulled from Honcho code with minor updates, reads local default
    environment variables from a .env file located in the project root
    directory and loads them into the OS environment.
    """
    try:
        with open(path) as f:
            content = f.read()
    except IOError:
        content = ''

    for line in content.splitlines():
        m1 = re.match(r'\A([A-Za-z_0-9]+)=(.*)\Z', line)
        if m1:
            key, val = m1.group(1), m1.group(2)
            m2 = re.match(r"\A'(.*)'\Z", val)
            if m2:
                val = m2.group(1)
            m3 = re.match(r'\A"(.*)"\Z', val)
            if m3:
                val = re.sub(r'\\(.)', r'\1', m3.group(1))
            os.environ.setdefault(key, val)


def load_fixture(file):
    fixtures_folder = os.path.abspath(
        os.path.join(__file__, os.pardir, os.pardir, 'tests', 'fixtures')
    )
    with open(os.path.join(fixtures_folder, file)) as fixture:
        return json.loads(fixture.read())
