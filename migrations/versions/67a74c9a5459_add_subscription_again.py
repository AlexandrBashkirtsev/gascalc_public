"""add subscription again

Revision ID: 67a74c9a5459
Revises: ad312c289ecd
Create Date: 2020-09-11 16:34:25.243416

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '67a74c9a5459'
down_revision = 'ad312c289ecd'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('subscription', sa.String(length=120), server_default='demo', nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'subscription')
    # ### end Alembic commands ###