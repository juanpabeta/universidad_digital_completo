"""Initial schema matching Module 9's entity and relationship design."""

from alembic import op
import sqlalchemy as sa


revision = "001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "roles",
        sa.Column("id_rol", sa.Integer(), primary_key=True),
        sa.Column("nombre", sa.String(20), nullable=False, unique=True),
        sa.Column("descripcion", sa.String(150), nullable=False),
    )
    op.create_table(
        "usuarios",
        sa.Column("id_usuario", sa.Integer(), primary_key=True),
        sa.Column("nombres", sa.String(100), nullable=False),
        sa.Column("apellidos", sa.String(100), nullable=False),
        sa.Column("email", sa.String(254), nullable=False, unique=True),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("activo", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column(
            "fecha_creacion", sa.DateTime(timezone=True),
            nullable=False, server_default=sa.func.now(),
        ),
    )
    op.create_table(
        "usuario_rol",
        sa.Column(
            "id_usuario", sa.Integer(), sa.ForeignKey("usuarios.id_usuario", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column(
            "id_rol", sa.Integer(), sa.ForeignKey("roles.id_rol", ondelete="CASCADE"),
            primary_key=True,
        ),
    )
    op.create_table(
        "materias",
        sa.Column("id_materia", sa.Integer(), primary_key=True),
        sa.Column("nombre", sa.String(150), nullable=False),
        sa.Column("codigo", sa.String(30), nullable=False, unique=True),
        sa.Column("creditos", sa.Integer(), nullable=False),
        sa.Column("activa", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column(
            "id_docente", sa.Integer(),
            sa.ForeignKey("usuarios.id_usuario", ondelete="RESTRICT"), nullable=True,
        ),
        sa.CheckConstraint("creditos > 0", name="ck_materias_creditos"),
    )
    op.create_table(
        "periodos_academicos",
        sa.Column("id_periodo", sa.Integer(), primary_key=True),
        sa.Column("nombre", sa.String(30), nullable=False, unique=True),
        sa.Column("fecha_inicio", sa.Date(), nullable=False),
        sa.Column("fecha_fin", sa.Date(), nullable=False),
        sa.Column("estado", sa.String(10), nullable=False, server_default="ABIERTO"),
        sa.CheckConstraint("fecha_fin >= fecha_inicio", name="ck_periodos_fechas"),
        sa.CheckConstraint("estado IN ('ABIERTO','CERRADO')", name="ck_periodos_estado"),
    )
    op.create_table(
        "inscripciones",
        sa.Column("id_inscripcion", sa.Integer(), primary_key=True),
        sa.Column("id_usuario", sa.Integer(), sa.ForeignKey("usuarios.id_usuario"), nullable=False),
        sa.Column("id_materia", sa.Integer(), sa.ForeignKey("materias.id_materia"), nullable=False),
        sa.Column(
            "id_periodo", sa.Integer(), sa.ForeignKey("periodos_academicos.id_periodo"),
            nullable=False,
        ),
        sa.Column(
            "fecha_inscripcion", sa.DateTime(timezone=True),
            nullable=False, server_default=sa.func.now(),
        ),
        sa.Column("estado", sa.String(10), nullable=False, server_default="ACTIVA"),
        sa.UniqueConstraint("id_usuario", "id_materia", "id_periodo", name="uq_inscripcion_unica"),
        sa.CheckConstraint("estado IN ('ACTIVA','CANCELADA')", name="ck_inscripcion_estado"),
    )
    op.create_index("ix_inscripciones_materia_periodo", "inscripciones", ["id_materia", "id_periodo"])
    op.create_table(
        "calificaciones",
        sa.Column("id_calificacion", sa.Integer(), primary_key=True),
        sa.Column(
            "id_inscripcion", sa.Integer(),
            sa.ForeignKey("inscripciones.id_inscripcion"), nullable=False,
        ),
        sa.Column("nota", sa.Numeric(5, 2), nullable=False),
        sa.Column("tipo", sa.String(20), nullable=False),
        sa.Column(
            "fecha_registro", sa.DateTime(timezone=True),
            nullable=False, server_default=sa.func.now(),
        ),
        sa.CheckConstraint("nota >= 0 AND nota <= 100", name="ck_calificaciones_nota"),
        sa.CheckConstraint(
            "tipo IN ('PARCIAL','FINAL','RECUPERACION')", name="ck_calificaciones_tipo"
        ),
    )
    op.create_index("ix_calificaciones_inscripcion", "calificaciones", ["id_inscripcion"])


def downgrade() -> None:
    op.drop_index("ix_calificaciones_inscripcion", table_name="calificaciones")
    op.drop_table("calificaciones")
    op.drop_index("ix_inscripciones_materia_periodo", table_name="inscripciones")
    op.drop_table("inscripciones")
    op.drop_table("periodos_academicos")
    op.drop_table("materias")
    op.drop_table("usuario_rol")
    op.drop_table("usuarios")
    op.drop_table("roles")
