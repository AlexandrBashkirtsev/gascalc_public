"""remove subscription again

Revision ID: ad312c289ecd
Revises: b1b18572a9b0
Create Date: 2020-09-11 16:33:14.307790

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'ad312c289ecd'
down_revision = 'b1b18572a9b0'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'subscription')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('subscription', mysql.VARCHAR(length=120), nullable=True))
    # ### end Alembic commands ###
