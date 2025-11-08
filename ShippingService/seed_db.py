import os
import sys
import django
import csv
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

# --- Setup Django environment first ---
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'ShippingService'))
sys.path.insert(0, PROJECT_ROOT)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ShippingService.settings')
django.setup()  # Must be called before importing models

# --- Now import Django models ---
from shippingapp.models import Shipment
from shippingapp.Status.shipping_status import ShippingStatus

# --- CSV file path ---
CSV_FILE_PATH = os.path.join(BASE_DIR, "SeedData", "eci_shipments.csv")

# --- Helper function ---
def parse_datetime(value):
    if not value:
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        return None

# --- Seed function ---
def seed_shipments():
    # Truncate table
    Shipment.objects.all().delete()
    print("Truncated Shipment table.")

    with open(CSV_FILE_PATH, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            shipment = Shipment.objects.create(
                tracking_no=row['tracking_no'],
                order_id=int(row['order_id']),
                carrier=row['carrier'],
                status=row['status'] if row['status'] in [s.value for s in ShippingStatus] else ShippingStatus.PENDING.value,
                shipped_at=parse_datetime(row.get('shipped_at')),
                delivered_at=parse_datetime(row.get('delivered_at')),
            )
            print(f"Created shipment: {shipment.tracking_no}")

if __name__ == "__main__":
    seed_shipments()
    print("Seed complete!")
