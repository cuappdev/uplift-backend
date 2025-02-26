from app_factory import create_app

# Create Flask app with scrapers enabled
app = create_app(run_migrations=False)

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000)
