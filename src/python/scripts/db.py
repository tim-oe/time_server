"""
Database Scripts

Custom tasks for database operations.
"""

import os
import subprocess
import sys


def migrate():
    """Run Django database migrations."""
    print("🗄️ Running database migrations...")
    try:
        subprocess.run(
            ["poetry", "run", "python", "manage.py", "makemigrations"], check=True
        )
        subprocess.run(["poetry", "run", "python", "manage.py", "migrate"], check=True)
        print("✅ Database migrations completed")
    except subprocess.CalledProcessError as e:
        print(f"❌ Migration failed: {e}")
        sys.exit(1)


def reset_database():
    """Reset the database (WARNING: Destructive operation)."""
    print("⚠️ WARNING: This will delete all data!")
    response = input("Are you sure you want to reset the database? (yes/no): ")

    if response.lower() != "yes":
        print("❌ Database reset cancelled")
        return

    print("🗄️ Resetting database...")
    try:
        # Remove database file
        if os.path.exists("db.sqlite3"):
            os.remove("db.sqlite3")
            print("✅ Database file removed")

        # Run migrations
        subprocess.run(["poetry", "run", "python", "manage.py", "migrate"], check=True)
        print("✅ Database reset completed")
    except subprocess.CalledProcessError as e:
        print(f"❌ Database reset failed: {e}")
        sys.exit(1)


def seed_database():
    """Seed the database with sample data."""
    print("🌱 Seeding database with sample data...")
    try:
        subprocess.run(
            [
                "poetry",
                "run",
                "python",
                "manage.py",
                "loaddata",
                "fixtures/sample_data.json",
            ],
            check=True,
        )
        print("✅ Database seeded successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Database seeding failed: {e}")
        print("💡 Create fixtures/sample_data.json with your sample data")
        sys.exit(1)


def create_superuser():
    """Create a Django superuser."""
    print("👤 Creating superuser...")
    try:
        subprocess.run(
            ["poetry", "run", "python", "manage.py", "createsuperuser"], check=True
        )
        print("✅ Superuser created successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Superuser creation failed: {e}")
        sys.exit(1)


def backup_database():
    """Backup the database."""
    print("💾 Backing up database...")
    try:
        date_output = (
            subprocess.check_output(["date", "+%Y%m%d_%H%M%S"]).decode().strip()
        )
        backup_file = f"backup_{date_output}.sqlite3"
        subprocess.run(["cp", "db.sqlite3", f"backups/{backup_file}"], check=True)
        print(f"✅ Database backed up to backups/{backup_file}")
    except subprocess.CalledProcessError as e:
        print(f"❌ Database backup failed: {e}")
        sys.exit(1)
