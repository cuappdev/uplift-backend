from app_factory import create_app
import sentry_sdk
import os

# Initialize Sentry only if not in local
if os.environ.get('FLASK_ENV') in ["development", "production"]:
    sentry_sdk.init(
        dsn="https://2a96f65cca45d8a7c3ffc3b878d4346b@o4507365244010496.ingest.us.sentry.io/4507850536386560",
        traces_sample_rate=1.0,
        profiles_sample_rate=1.0,
    )

# Create Flask app with scrapers enabled
app = create_app(run_migrations=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
