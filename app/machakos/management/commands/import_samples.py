import json
from django.core.management.base import BaseCommand
from app.machakos.models import SoilSample
from datetime import datetime


class Command(BaseCommand):

    help = "Import soil samples from JSON"

    def handle(self, *args, **kwargs):

        with open(r"E:\Projects\Soil Samples Data\Samples json\machakosdata.json") as f:
            data = json.load(f)

        for record in data:

            date_received = datetime.fromtimestamp(
                record["_submission_time"] / 1000
            ).date()

            SoilSample.objects.create(

                town=record.get("Get selected Agripreneur Ward from the Agripreneurs List"),

                latitude=record.get("_Record the GPS Coordinates_latitude"),
                longitude=record.get("_Record the GPS Coordinates_longitude"),
                altitude=record.get("_Record the GPS Coordinates_altitude"),

                sample_id=record.get("Provide the ID of the designated sampling point (SP-ID).1"),

                date_sample_received=date_received
            )

        self.stdout.write(self.style.SUCCESS("Data imported successfully"))