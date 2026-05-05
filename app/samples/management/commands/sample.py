import json
import os
from pathlib import Path
from django.core.management.base import BaseCommand
from app.samples.models import SoilSample
from datetime import datetime


class Command(BaseCommand):
    help = "Import soil samples from JSON files (select multiple files from directory)"

    def add_arguments(self, parser):
        parser.add_argument(
            '--files',
            nargs='+',
            type=str,
            help='Specific JSON filenames to import (space-separated). If not provided, you can select interactively.',
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Import all JSON files in the directory',
        )

    def handle(self, *args, **kwargs):
        try:
            folder_path = Path(r"D:\Projects\Soil Samples Data\Samples json")
            
            # Find all JSON files in the directory
            all_json_files = sorted(list(folder_path.glob("*.json")))
            
            if not all_json_files:
                self.stdout.write(
                    self.style.ERROR(f"No JSON files found in {folder_path}")
                )
                return
            
            # Determine which files to process
            files_to_process = []
            
            if kwargs.get('all'):
                # Import all files
                files_to_process = all_json_files
                self.stdout.write(f"Processing all {len(files_to_process)} JSON files")
                
            elif kwargs.get('files'):
                # Import specified files
                for filename in kwargs['files']:
                    file_path = folder_path / filename
                    if file_path.exists() and file_path.suffix == '.json':
                        files_to_process.append(file_path)
                    else:
                        self.stdout.write(
                            self.style.WARNING(f"File not found or not JSON: {filename}")
                        )
                
                if not files_to_process:
                    self.stdout.write(
                        self.style.ERROR("None of the specified files were valid JSON files")
                    )
                    return
                    
            else:
                # Interactive selection
                self.stdout.write(f"\n{'='*60}")
                self.stdout.write(f"Found {len(all_json_files)} JSON files in:")
                self.stdout.write(f"  {folder_path}")
                self.stdout.write(f"{'='*60}")
                
                for i, file in enumerate(all_json_files, 1):
                    size_kb = file.stat().st_size / 1024
                    modified_time = datetime.fromtimestamp(file.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
                    self.stdout.write(f"  [{i}] {file.name} ({size_kb:.1f} KB, modified: {modified_time})")
                
                self.stdout.write(f"  [A] Import ALL files")
                self.stdout.write(f"  [0] Cancel")
                self.stdout.write(f"{'='*60}")
                
                # Get user input
                while True:
                    try:
                        choice = input("\nEnter file numbers (comma-separated), 'A' for all, or '0' to cancel: ").strip()
                        
                        if choice.upper() == 'A':
                            files_to_process = all_json_files
                            self.stdout.write(f"Selected all {len(files_to_process)} files")
                            break
                        elif choice == '0':
                            self.stdout.write("Import cancelled")
                            return
                        else:
                            # Parse comma-separated numbers
                            selected_indices = []
                            for part in choice.split(','):
                                part = part.strip()
                                if '-' in part:
                                    # Handle ranges like "1-3"
                                    start, end = part.split('-')
                                    selected_indices.extend(range(int(start), int(end) + 1))
                                else:
                                    selected_indices.append(int(part))
                            
                            # Validate and get files
                            for index in selected_indices:
                                if 1 <= index <= len(all_json_files):
                                    files_to_process.append(all_json_files[index - 1])
                                else:
                                    self.stdout.write(
                                        self.style.WARNING(f"Invalid index: {index} (must be 1-{len(all_json_files)})")
                                    )
                            
                            if files_to_process:
                                # Remove duplicates while preserving order
                                files_to_process = list(dict.fromkeys(files_to_process))
                                break
                            else:
                                self.stdout.write(
                                    self.style.WARNING("No valid files selected. Please try again.")
                                )
                    
                    except ValueError:
                        self.stdout.write(
                            self.style.WARNING("Invalid input. Please enter numbers, 'A', or '0'")
                        )
                    except KeyboardInterrupt:
                        self.stdout.write("\nImport cancelled")
                        return
            
            # Process each selected file
            total_records = 0
            total_success = 0
            total_duplicates = 0
            total_warnings = 0
            total_errors = 0
            
            for file_path in files_to_process:
                self.stdout.write(f"\n{'='*60}")
                self.stdout.write(f"Processing: {file_path.name}")
                self.stdout.write(f"{'='*60}")
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    self.stdout.write(f"Found {len(data)} records in this file...")
                    total_records += len(data)
                    
                    file_success = 0
                    file_duplicates = 0
                    file_warnings = 0
                    file_errors = 0
                    
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
                                        self.style.WARNING(f"  Record {index}: Invalid submission time format, setting to null")
                                    )
                                    file_warnings += 1
                            else:
                                date_received = None
                                file_warnings += 1

                            # Get sample_id
                            sample_id = record.get("Provide the ID of the designated sampling point (SP-ID).1")
                            
                            if not sample_id:
                                sample_id = f"{file_path.stem}-UNKNOWN-{index:03d}"
                                self.stdout.write(
                                    self.style.WARNING(f"  Record {index}: No sample_id found, using placeholder: {sample_id}")
                                )
                                file_warnings += 1
                            
                            # Check for duplicate sample_id
                            original_sample_id = sample_id
                            counter = 1
                            while SoilSample.objects.filter(sample_id=sample_id).exists():
                                sample_id = f"{original_sample_id}-{counter}"
                                counter += 1
                            
                            if original_sample_id != sample_id:
                                self.stdout.write(
                                    self.style.WARNING(f"  Record {index}: Duplicate sample ID '{original_sample_id}', changed to '{sample_id}'")
                                )
                                file_warnings += 1
                            
                            # Client information
                            client_name = record.get("client_name")
                            if client_name == "":
                                client_name = None
                            
                            client_phone = record.get("client_phone")
                            if client_phone == "":
                                client_phone = None
                            
                            # Location information
                            town = record.get("Get selected Agripreneur Ward from the Agripreneurs List")
                            if town == "":
                                town = None
                            
                            county = record.get("county")
                            if county == "":
                                county = None
                            
                            sub_county = record.get("sub_county")
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
                            
                            # Try to convert to float
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
                            previous_crop = record.get("previous_crop")
                            if previous_crop == "":
                                previous_crop = None
                            
                            next_crop = record.get("next_crop")
                            if next_crop == "":
                                next_crop = None
                            
                            # Create SoilSample record
                            soil_sample = SoilSample.objects.create(
                                client_name=client_name,
                                client_phone=client_phone,
                                town=town,
                                county=county,
                                sub_county=sub_county,
                                latitude=latitude,
                                longitude=longitude,
                                altitude=altitude,
                                sample_id=sample_id,
                                previous_crop=previous_crop,
                                next_crop=next_crop,
                                date_sample_received=date_received,
                                test_required="Soil Test"
                            )
                            
                            file_success += 1
                            
                            # Show summary of null fields
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
                                    f"  ✓ Record {index}: {sample_id} (null: {', '.join(null_fields)})"
                                )
                            else:
                                self.stdout.write(f"  ✓ Record {index}: {sample_id}")
                            
                        except Exception as e:
                            self.stdout.write(
                                self.style.ERROR(f"  ✗ Record {index}: Error - {str(e)}")
                            )
                            file_errors += 1
                    
                    # File summary
                    self.stdout.write(f"\n  {'─'*50}")
                    self.stdout.write(f"  File Summary for {file_path.name}:")
                    self.stdout.write(f"  ├─ Records processed: {len(data)}")
                    self.stdout.write(f"  ├─ Successfully imported: {file_success}")
                    self.stdout.write(f"  ├─ Warnings (null/placeholder): {file_warnings}")
                    self.stdout.write(f"  └─ Errors: {file_errors}")
                    
                    total_success += file_success
                    total_duplicates += file_duplicates
                    total_warnings += file_warnings
                    total_errors += file_errors
                    
                except json.JSONDecodeError as e:
                    self.stdout.write(
                        self.style.ERROR(f"Invalid JSON in {file_path.name}: {str(e)}")
                    )
                    total_errors += 1
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f"Error processing {file_path.name}: {str(e)}")
                    )
                    total_errors += 1
            
            # Final grand summary
            self.stdout.write(f"\n{'='*60}")
            self.stdout.write(f"GRAND TOTAL SUMMARY")
            self.stdout.write(f"{'='*60}")
            self.stdout.write(f"Files processed: {len(files_to_process)}")
            self.stdout.write(f"Total records in all files: {total_records}")
            self.stdout.write(f"Successfully imported: {total_success}")
            self.stdout.write(f"Warnings (null values/placeholders): {total_warnings}")
            self.stdout.write(f"Errors: {total_errors}")
            self.stdout.write(f"{'='*60}")
            
        except FileNotFoundError:
            self.stdout.write(
                self.style.ERROR("Directory not found. Please check the folder path.")
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"Unexpected error: {str(e)}")
            )