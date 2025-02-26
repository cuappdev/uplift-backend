from app_factory import create_app

# Create Flask app for migrations only (no scrapers)
app = create_app(run_migrations=True)
