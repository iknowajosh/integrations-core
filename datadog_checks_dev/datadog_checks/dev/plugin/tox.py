# (C) Datadog, Inc. 2019
# All rights reserved
# Licensed under a 3-clause BSD style license (see LICENSE)
from __future__ import absolute_import

import tox
import tox.config

STYLE_ENV_NAME = 'style'
STYLE_FLAG = 'check_dd_style'


@tox.hookimpl
def tox_configure(config):
    """
    For more info, see: https://tox.readthedocs.io/en/latest/plugins.html
    For an example, see: https://github.com/tox-dev/tox-travis
    """
    sections = config._cfg.sections

    # Default to false so:
    # 1. we don't affect other projects using tox
    # 2. check migrations can happen gradually
    if str(sections.get('testenv', {}).get(STYLE_FLAG, 'false')).lower() == 'true':
        add_style_env(config, sections)


def add_style_env(config, sections):
    # testenv:style
    section = '{}{}'.format(tox.config.testenvprefix, STYLE_ENV_NAME)
    sections[section] = {
        # black only supports Python 3+
        # isort also https://github.com/timothycrosley/isort/issues/760#issuecomment-471851370
        'basepython': 'python3',
        'skip_install': 'true',
        'deps': 'flake8\nblack\nisort>=4.3.15',
        'commands': 'flake8 .\nblack --check --diff .\nisort --check-only --diff --recursive .',
    }

    # Disable flake8 since we already include that
    config.envlist[:] = [env for env in config.envlist if not env.endswith('flake8')]

    # Add the style environment
    config.envlist.append(STYLE_ENV_NAME)

    # This is just boilerplate necessary to create a valid reader
    reader = tox.config.SectionReader('tox', config._cfg)
    reader.addsubstitutions(toxinidir=config.toxinidir, homedir=config.homedir)
    reader.addsubstitutions(toxworkdir=config.toxworkdir)
    config.distdir = reader.getpath('distdir', '{toxworkdir}/dist')
    reader.addsubstitutions(distdir=config.distdir)
    config.distshare = reader.getpath('distshare', '{homedir}/.tox/distshare')
    reader.addsubstitutions(distshare=config.distshare)

    make_envconfig = tox.config.ParseIni.make_envconfig
    # Make this a non-bound function for Python 2 compat
    make_envconfig = getattr(make_envconfig, '__func__', make_envconfig)

    config.envconfigs[STYLE_ENV_NAME] = make_envconfig(config, STYLE_ENV_NAME, section, reader._subs, config)
