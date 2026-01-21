"""initial

Revision ID: 0001_initial
Revises: 
Create Date: 2026-01-21T16:17:41.485518Z
"""

from alembic import op
import sqlalchemy as sa

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("nombre", sa.String(length=120), nullable=False),
        sa.Column("apellido", sa.String(length=120), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("cedula", sa.String(length=10), nullable=False),
        sa.Column("telefono", sa.String(length=10), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("role", sa.String(length=20), nullable=False, server_default="cliente"),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)
    op.create_index("ix_users_cedula", "users", ["cedula"], unique=True)

    op.create_table(
        "room_types",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("tipo", sa.String(length=20), nullable=False),
        sa.Column("capacidad_personas", sa.Integer(), nullable=False),
        sa.Column("precio_noche", sa.Numeric(10, 2), nullable=False),
    )
    op.create_unique_constraint("uq_room_types_tipo", "room_types", ["tipo"])

    op.create_table(
        "rooms",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("numero", sa.String(length=20), nullable=False),
        sa.Column("piso", sa.Integer(), nullable=False),
        sa.Column("estado", sa.String(length=20), nullable=False, server_default="disponible"),
        sa.Column("room_type_id", sa.Integer(), sa.ForeignKey("room_types.id", ondelete="RESTRICT"), nullable=False),
    )
    op.create_index("ix_rooms_numero", "rooms", ["numero"], unique=True)

    op.create_table(
        "reservations",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("room_id", sa.Integer(), sa.ForeignKey("rooms.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("fecha_inicio", sa.Date(), nullable=False),
        sa.Column("fecha_fin", sa.Date(), nullable=False),
        sa.Column("costo_total", sa.Numeric(10, 2), nullable=False),
        sa.Column("reporte_path", sa.String(length=500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="pending"),
        sa.Column("paypal_order_id", sa.String(length=80), nullable=True),
        sa.Column("paypal_capture_id", sa.String(length=80), nullable=True),
    )
    op.create_index("ix_reservations_paypal_order_id", "reservations", ["paypal_order_id"], unique=False)
    op.create_index("ix_reservations_paypal_capture_id", "reservations", ["paypal_capture_id"], unique=False)

def downgrade():
    op.drop_index("ix_reservations_paypal_capture_id", table_name="reservations")
    op.drop_index("ix_reservations_paypal_order_id", table_name="reservations")
    op.drop_table("reservations")

    op.drop_index("ix_rooms_numero", table_name="rooms")
    op.drop_table("rooms")

    op.drop_constraint("uq_room_types_tipo", "room_types", type_="unique")
    op.drop_table("room_types")

    op.drop_index("ix_users_cedula", table_name="users")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
