"""initial schema

Revision ID: 0001
Revises:
Create Date: 2026-10-07
"""
from alembic import op
import sqlalchemy as sa


revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("username", sa.String(64), nullable=False, unique=True),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("role", sa.String(32), nullable=False, server_default="USER"),
        sa.Column("created_date", sa.DateTime, nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_users_username", "users", ["username"])

    op.create_table(
        "requests",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("request_type", sa.String(32), nullable=False),
        sa.Column("status", sa.String(32), nullable=False, server_default="SUBMITTED"),
        sa.Column("created_by", sa.Integer, sa.ForeignKey("users.id"), nullable=False),
        sa.Column("created_date", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("updated_date", sa.DateTime, nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_requests_request_type", "requests", ["request_type"])
    op.create_index("ix_requests_status", "requests", ["status"])

    op.create_table(
        "approvals",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("request_id", sa.Integer, sa.ForeignKey("requests.id"), nullable=False),
        sa.Column("approved_by", sa.Integer, sa.ForeignKey("users.id"), nullable=False),
        sa.Column("approval_status", sa.String(32), nullable=False),
        sa.Column("comments", sa.Text, nullable=True),
        sa.Column("approved_date", sa.DateTime, nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_approvals_request_id", "approvals", ["request_id"])

    op.create_table(
        "audit_log",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("username", sa.String(64), nullable=False),
        sa.Column("action", sa.String(64), nullable=False),
        sa.Column("entity_type", sa.String(64), nullable=False),
        sa.Column("entity_id", sa.Integer, nullable=True),
        sa.Column("timestamp", sa.DateTime, nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_audit_log_username", "audit_log", ["username"])
    op.create_index("ix_audit_log_action", "audit_log", ["action"])
    op.create_index("ix_audit_log_entity_type", "audit_log", ["entity_type"])
    op.create_index("ix_audit_log_timestamp", "audit_log", ["timestamp"])

    op.create_table(
        "notifications",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("request_id", sa.Integer, sa.ForeignKey("requests.id"), nullable=False),
        sa.Column("recipient", sa.String(255), nullable=False),
        sa.Column("message", sa.Text, nullable=False),
        sa.Column("status", sa.String(32), nullable=False, server_default="PENDING"),
        sa.Column("created_date", sa.DateTime, nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_notifications_request_id", "notifications", ["request_id"])
    op.create_index("ix_notifications_status", "notifications", ["status"])


def downgrade() -> None:
    op.drop_index("ix_notifications_status", table_name="notifications")
    op.drop_index("ix_notifications_request_id", table_name="notifications")
    op.drop_table("notifications")

    op.drop_index("ix_audit_log_timestamp", table_name="audit_log")
    op.drop_index("ix_audit_log_entity_type", table_name="audit_log")
    op.drop_index("ix_audit_log_action", table_name="audit_log")
    op.drop_index("ix_audit_log_username", table_name="audit_log")
    op.drop_table("audit_log")

    op.drop_index("ix_approvals_request_id", table_name="approvals")
    op.drop_table("approvals")

    op.drop_index("ix_requests_status", table_name="requests")
    op.drop_index("ix_requests_request_type", table_name="requests")
    op.drop_table("requests")

    op.drop_index("ix_users_username", table_name="users")
    op.drop_table("users")
