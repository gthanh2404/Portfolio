"""Give the app a dummy DATABASE_URL so tests can run without a database."""

import os

os.environ.setdefault("DATABASE_URL", "postgresql://app:unused@localhost:5432/appdb")
