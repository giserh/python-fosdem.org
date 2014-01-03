"""add_is_backup_to_event

Revision ID: 505416a7557b
Revises: 1ba6fa8d2ea9
Create Date: 2014-01-03 11:18:17.903095

"""

# revision identifiers, used by Alembic.
revision = '505416a7557b'
down_revision = '1ba6fa8d2ea9'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('talk', sa.Column('is_backup', sa.Boolean()))


def downgrade():
    op.drop_column('talk', 'is_backup')
