import json
from django.core.management.base import BaseCommand
from kitui.models import SoilSample
from datetime import datetime


class Command(BaseCommand):
    help = "Import soil samples from JSON (extracts all rows, even with null values)"

    def handle(self, *args, **kwargs):
        try:
            # Open and load JSON file
            with open(r"E:\Projects\Soil Samples Data\Samples json\kituidata.json", 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.stdout.write(f"Found {len(data)} records to process...")
            
            success_count = 0
            duplicate_count = 0
            warning_count = 0
            
            for index, record in enumerate(data, start=1):
                try:
                    # Convert submission time to date
                    submission_time = record.get("_submission_time")
                    if submission_time:
                        try:
                            date_received = datetime.fromtimestamp(submission_time / 1000).date()
                        except (TypeError, ValueError):
                            date_received = None
                            self.stdout.write(
                                self.style.WARNING(f"Record {index}: Invalid submission time format, setting to null")
                            )
                            warning_count += 1
                    else:
                        date_received = None
                        self.stdout.write(
                            self.style.WARNING(f"Record {index}: No submission time found, setting to null")
                        )
                        warning_count += 1

                    # Get sample_id - this is required by model (no null=True)
                    sample_id = record.get("Provide the ID of the designated sampling point (SP-ID).1")
                    
                    # If no sample_id, create a placeholder
                    if not sample_id:
                        sample_id = f"UNKNOWN-{index:03d}"
                        self.stdout.write(
                            self.style.WARNING(f"Record {index}: No sample_id found, using placeholder: {sample_id}")
                        )
                        warning_count += 1
                    
                    # Check for duplicate sample_id and handle it
                    original_sample_id = sample_id
                    counter = 1
                    while SoilSample.objects.filter(sample_id=sample_id).exists():
                        sample_id = f"{original_sample_id}-{counter}"
                        counter += 1
                    
                    if original_sample_id != sample_id:
                        self.stdout.write(
                            self.style.WARNING(f"Record {index}: Duplicate sample ID '{original_sample_id}', changed to '{sample_id}'")
                        )
                        warning_count += 1
                    
                    # Get all fields with null values allowed
                    
                    # Client information
                    client_name = record.get("client_name")  # Adjust field name as per your JSON
                    if client_name == "":
                        client_name = None
                    
                    client_phone = record.get("client_phone")  # Adjust field name as per your JSON
                    if client_phone == "":
                        client_phone = None
                    
                    # Location information
                    town = record.get("Get selected Agripreneur Ward from the Agripreneurs List")
                    if town == "":
                        town = None
                    
                    county = record.get("county")  # Adjust field name as per your JSON
                    if county == "":
                        county = None
                    
                    sub_county = record.get("sub_county")  # Adjust field name as per your JSON
                    if sub_county == "":
                        sub_county = None
                    
                    # GPS coordinates
                    latitude = record.get("_Record the GPS Coordinates_latitude")
                    longitude = record.get("_Record the GPS Coordinates_longitude")
                    altitude = record.get("_Record the GPS Coordinates_altitude")
                    
                    # Convert empty strings to None
                    if latitude == "":
                        latitude = None
                    if longitude == "":
                        longitude = None
                    if altitude == "":
                        altitude = None
                    
                    # Try to convert to float, keep None if conversion fails
                    try:
                        latitude = float(latitude) if latitude is not None else None
                    except (ValueError, TypeError):
                        latitude = None
                    
                    try:
                        longitude = float(longitude) if longitude is not None else None
                    except (ValueError, TypeError):
                        longitude = None
                    
                    try:
                        altitude = float(altitude) if altitude is not None else None
                    except (ValueError, TypeError):
                        altitude = None
                    
                    # Crop information
                    previous_crop = record.get("previous_crop")  # Adjust field name as per your JSON
                    if previous_crop == "":
                        previous_crop = None
                    
                    next_crop = record.get("next_crop")  # Adjust field name as per your JSON
                    if next_crop == "":
                        next_crop = None
                    
                    # Create SoilSample record - all null values will be saved as NULL in database
                    soil_sample = SoilSample.objects.create(
                        # Client information
                        client_name=client_name,
                        client_phone=client_phone,
                        
                        # Location information
                        town=town,
                        county=county,
                        sub_county=sub_county,
                        
                        # GPS coordinates
                        latitude=latitude,
                        longitude=longitude,
                        altitude=altitude,
                        
                        # Sample information
                        sample_id=sample_id,
                        
                        # Crop information
                        previous_crop=previous_crop,
                        next_crop=next_crop,
                        
                        # Date and test info
                        date_sample_received=date_received,
                        test_required="Soil Test"  # Default value
                    )
                    
                    success_count += 1
                    
                    # Show summary of what was imported
                    null_fields = []
                    if client_name is None:
                        null_fields.append("client_name")
                    if client_phone is None:
                        null_fields.append("client_phone")
                    if town is None:
                        null_fields.append("town")
                    if county is None:
                        null_fields.append("county")
                    if sub_county is None:
                        null_fields.append("sub_county")
                    if latitude is None:
                        null_fields.append("latitude")
                    if longitude is None:
                        null_fields.append("longitude")
                    if altitude is None:
                        null_fields.append("altitude")
                    if previous_crop is None:
                        null_fields.append("previous_crop")
                    if next_crop is None:
                        null_fields.append("next_crop")
                    if date_received is None:
                        null_fields.append("date_sample_received")
                    
                    if null_fields:
                        self.stdout.write(
                            f"Record {index}: Imported sample {sample_id} (null fields: {', '.join(null_fields)})"
                        )
                    else:
                        self.stdout.write(f"Record {index}: Imported sample {sample_id} (all fields present)")
                    
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f"Record {index}: Error importing record - {str(e)}")
                    )
                    duplicate_count += 1
            
            # Final summary
            self.stdout.write(
                self.style.SUCCESS(
                    f"\n{'='*50}\n"
                    f"Import Summary:\n"
                    f"{'='*50}\n"
                    f"Total records in file: {len(data)}\n"
                    f"Successfully imported: {success_count}\n"
                    f"Records with warnings (null values/placeholders): {warning_count}\n"
                    f"Failed imports: {duplicate_count}\n"
                    f"{'='*50}"
                )
            )
            
        except FileNotFoundError:
            self.stdout.write(
                self.style.ERROR("JSON file not found. Please check the file path.")
            )
        except json.JSONDecodeError as e:
            self.stdout.write(
                self.style.ERROR(f"Invalid JSON file: {str(e)}")
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"Unexpected error: {str(e)}")
            )