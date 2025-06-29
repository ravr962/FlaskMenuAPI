"""Add role column to User

Revision ID: e399105bb023
Revises: 7dbde4be086f
Create Date: 2025-06-26 13:58:24.462831

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision = 'e399105bb023'
down_revision = '7dbde4be086f'
branch_labels = None
depends_on = None


# def upgrade():
#     # ### commands auto generated by Alembic - please adjust! ###
#     with op.batch_alter_table('user', schema=None) as batch_op:
#         batch_op.add_column(sa.Column('role', sa.String(length=20), nullable=True))

#     # ### end Alembic commands ###

def upgrade():
    conn = op.get_bind()
    inspector = inspect(conn)

    existing_columns = [col['name'] for col in inspector.get_columns('user')]
    if 'role' not in existing_columns:
        with op.batch_alter_table('user', schema=None) as batch_op:
            batch_op.add_column(sa.Column('role', sa.String(length=20), nullable=True))


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_column('role')

    # ### end Alembic commands ###
