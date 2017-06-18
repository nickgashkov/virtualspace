from gettext import gettext as _

import sqlalchemy as sa
from sqlalchemy.orm import relationship

from virtualspace.models.base import BaseModel


class Account(BaseModel):
    __abstract__ = False

    role_id = sa.Column(
        sa.Integer,
        sa.ForeignKey('role.id'),
        info={'verbose_name': _('role')}
    )

    is_active = sa.Column(sa.Boolean, nullable=False, default=True, info={'verbose_name': _('is active')})

    nickname = sa.Column(sa.Unicode(128), nullable=False, info={'verbose_name': _('nickname')})
    email = sa.Column(sa.Unicode(128), nullable=False, info={'verbose_name': _('email')})
    password = sa.Column(sa.Unicode(128), nullable=False, info={'verbose_name': _('password')})

    first_name = sa.Column(sa.Unicode(128), info={'verbose_name': _('first name')})
    patr_name = sa.Column(sa.Unicode(128), info={'verbose_name': _('patr name')})
    last_name = sa.Column(sa.Unicode(128), info={'verbose_name': _('last name')})

    role = relationship('Role', backref='accounts')
