# Copyright (c) 2017 Nick Gashkov
#
# Distributed under MIT License. See LICENSE file for details.

import sqlalchemy as sa

from virtualspace.utils.models.bases import BaseModel
from virtualspace.utils.translation import gettext as _


class Triplet(BaseModel):
    __abstract__ = False

    prefix = sa.Column(sa.Unicode(16), nullable=False, info={'verbose_name': _('prefix')})
    name = sa.Column(sa.Unicode(128), nullable=False, info={'verbose_name': _('name')})
    value = sa.Column(sa.Unicode(512), nullable=False, info={'verbose_name': _('value')})

    kind = sa.Column(sa.Unicode(128), nullable=False, info={'verbose_name': _('kind')})
