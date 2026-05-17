"""
Seed default tenant and users.
Run with: flask seed-users
"""
import click
from flask.cli import with_appcontext
from app.utils.db import db
from app.models.tenant_model import Tenant
from app.models.user_model import User


def register_user_seed_commands(app):
    """Register user seed CLI commands."""

    @app.cli.command('seed-users')
    @with_appcontext
    def seed_users():
        """Create default tenant with super-admin and admin users."""
        click.echo('Seeding default users...')

        # Create or get default tenant
        tenant = Tenant.query.filter_by(slug='autoshkolla-demo').first()
        if not tenant:
            tenant = Tenant(
                name='AutoShkolla Demo',
                slug='autoshkolla-demo',
                email='info@autoshkolla-demo.com',
                phone='+383 44 000 000',
                address='Prishtinë, Kosovë',
                city='Prishtinë',
                representative='Admin',
                is_active=True,
            )
            db.session.add(tenant)
            db.session.flush()
            click.echo(f'  Created tenant: {tenant.name}')
        else:
            click.echo(f'  Tenant already exists: {tenant.name}')

        # Create super-admin
        super_admin = User.query.filter_by(
            tenant_id=tenant.id, username='superadmin'
        ).first()
        if not super_admin:
            super_admin = User(
                tenant_id=tenant.id,
                username='superadmin',
                full_name='Super Admin',
                email='superadmin@autoshkolla.com',
                role='super_admin',
                is_active=True,
            )
            super_admin.set_password('admin123')
            db.session.add(super_admin)
            click.echo('  Created super-admin: superadmin / admin123')
        else:
            click.echo('  Super-admin already exists')

        # Create regular admin
        admin = User.query.filter_by(
            tenant_id=tenant.id, username='admin'
        ).first()
        if not admin:
            admin = User(
                tenant_id=tenant.id,
                username='admin',
                full_name='Administrator',
                email='admin@autoshkolla.com',
                role='administrator',
                is_active=True,
            )
            admin.set_password('admin123')
            db.session.add(admin)
            click.echo('  Created admin: admin / admin123')
        else:
            click.echo('  Admin already exists')

        db.session.commit()
        click.echo('User seed complete!')
        click.echo('')
        click.echo('Login credentials:')
        click.echo('  Super Admin:   superadmin / admin123')
        click.echo('  Administrator: admin / admin123')
