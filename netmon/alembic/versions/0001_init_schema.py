from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB, TIMESTAMP

revision = "0001_init_schema"
down_revision = None

def upgrade():
    op.execute("CREATE EXTENSION IF NOT EXISTS timescaledb;")

    op.create_table(
        "devices",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("gns3_id", sa.String(64), index=True),
        sa.Column("name", sa.String(128), index=True, nullable=False),
        sa.Column("mgmt_ip", sa.String(64), index=True),
        sa.Column("dtype", sa.String(32), index=True),
        sa.Column("labels", JSONB, server_default="{}"),
        sa.Column("enabled", sa.Boolean, server_default=sa.text("true")),
    )

    op.create_table(
        "links",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("gns3_id", sa.String(64), index=True),
        sa.Column("a_dev_id", sa.Integer, sa.ForeignKey("devices.id")),
        sa.Column("b_dev_id", sa.Integer, sa.ForeignKey("devices.id")),
        sa.Column("a_if", sa.String(64)),
        sa.Column("b_if", sa.String(64)),
        sa.Column("meta", JSONB, server_default="{}"),
    )

    op.create_table(
        "checks",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("device_id", sa.Integer, sa.ForeignKey("devices.id"), index=True),
        sa.Column("ctype", sa.String(32), index=True),
        sa.Column("params", JSONB, server_default="{}"),
        sa.Column("interval_s", sa.Integer, nullable=False),
        sa.Column("enabled", sa.Boolean, server_default=sa.text("true")),
    )

    op.create_table(
        "alerts",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("device_id", sa.Integer, sa.ForeignKey("devices.id"), index=True),
        sa.Column("check_id", sa.Integer, sa.ForeignKey("checks.id"), index=True),
        sa.Column("rule", sa.String(128)),
        sa.Column("state", sa.String(16), index=True),
        sa.Column("last_change", TIMESTAMP(timezone=True)),
        sa.Column("acked_by", sa.String(64)),
        sa.Column("acked_at", TIMESTAMP(timezone=True)),
    )

    op.create_table(
        "silences",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("scope", JSONB, nullable=False),
        sa.Column("starts_at", TIMESTAMP(timezone=True), nullable=False),
        sa.Column("ends_at", TIMESTAMP(timezone=True), nullable=False),
        sa.Column("reason", sa.String(256)),
    )

    op.create_table(
        "audit_logs",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("actor", sa.String(64)),
        sa.Column("action", sa.String(64)),
        sa.Column("meta", JSONB, server_default="{}"),
        sa.Column("ts", TIMESTAMP(timezone=True), server_default=sa.text("now()")),
    )

    op.create_table(
        "metrics_raw",
        sa.Column("device_id", sa.Integer, sa.ForeignKey("devices.id"), nullable=False),
        sa.Column("check_id", sa.Integer, sa.ForeignKey("checks.id"), nullable=False),
        sa.Column("ts", TIMESTAMP(timezone=True), nullable=False),
        sa.Column("name", sa.String(64), nullable=False),
        sa.Column("value", sa.Float, nullable=False),
        sa.Column("labels", JSONB, server_default="{}"),
    )
    op.execute("SELECT create_hypertable('metrics_raw','ts',if_not_exists=>TRUE);")

    op.execute(
        """
      CREATE MATERIALIZED VIEW IF NOT EXISTS metrics_1m_avg
      WITH (timescaledb.continuous) AS
      SELECT time_bucket('1 minute', ts) AS bucket, device_id, name,
             avg(value) AS avg_value
      FROM metrics_raw
      GROUP BY bucket, device_id, name;
    """
    )
    op.execute(
        """
      CREATE MATERIALIZED VIEW IF NOT EXISTS metrics_5m_p95
      WITH (timescaledb.continuous) AS
      SELECT time_bucket('5 minutes', ts) AS bucket, device_id, name,
             approx_percentile(0.95, value) AS p95_value
      FROM metrics_raw
      GROUP BY bucket, device_id, name;
    """
    )


def downgrade():
    op.execute("DROP MATERIALIZED VIEW IF EXISTS metrics_5m_p95;")
    op.execute("DROP MATERIALIZED VIEW IF EXISTS metrics_1m_avg;")
    op.drop_table("metrics_raw")
    op.drop_table("audit_logs")
    op.drop_table("silences")
    op.drop_table("alerts")
    op.drop_table("checks")
    op.drop_table("links")
    op.drop_table("devices")