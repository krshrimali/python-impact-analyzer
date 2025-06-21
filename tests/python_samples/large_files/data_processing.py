# Large Python file with many functions and complex dependencies
# This file simulates a data processing pipeline with multiple stages

import os
import json
import random
import time
from typing import List, Dict, Any, Tuple, Optional, Union, Callable

# Constants
MAX_RETRY_COUNT = 5
DEFAULT_BATCH_SIZE = 100
CACHE_EXPIRY_SECONDS = 3600
LOG_LEVELS = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

# Global cache
_cache = {}

# Utility functions
def generate_unique_id() -> str:
    """Generate a unique identifier."""
    return f"{int(time.time())}-{random.randint(1000, 9999)}"

def log_message(level: str, message: str) -> None:
    """Log a message with the specified level."""
    if level not in LOG_LEVELS:
        level = "INFO"
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [{level}] {message}")

def retry_operation(operation: Callable, max_retries: int = MAX_RETRY_COUNT) -> Any:
    """Retry an operation with exponential backoff."""
    retry_count = 0
    last_exception = None
    
    while retry_count < max_retries:
        try:
            return operation()
        except Exception as e:
            last_exception = e
            retry_count += 1
            wait_time = 2 ** retry_count
            log_message("WARNING", f"Operation failed, retrying in {wait_time} seconds. Error: {str(e)}")
            time.sleep(wait_time)
    
    log_message("ERROR", f"Operation failed after {max_retries} retries. Last error: {str(last_exception)}")
    raise last_exception

def cache_result(key: str, value: Any) -> None:
    """Cache a result with expiry time."""
    _cache[key] = {
        "value": value,
        "expiry": time.time() + CACHE_EXPIRY_SECONDS
    }

def get_cached_result(key: str) -> Optional[Any]:
    """Get a cached result if it exists and is not expired."""
    if key in _cache:
        cache_entry = _cache[key]
        if time.time() < cache_entry["expiry"]:
            return cache_entry["value"]
        else:
            del _cache[key]
    return None

# Data validation functions
def validate_input_data(data: Dict[str, Any]) -> bool:
    """Validate input data structure."""
    required_fields = ["id", "timestamp", "payload"]
    for field in required_fields:
        if field not in data:
            log_message("ERROR", f"Missing required field: {field}")
            return False
    
    if not isinstance(data["payload"], dict):
        log_message("ERROR", "Payload must be a dictionary")
        return False
    
    return True

def validate_numeric_field(value: Any) -> bool:
    """Validate that a field is numeric."""
    try:
        float(value)
        return True
    except (ValueError, TypeError):
        return False

def validate_string_field(value: Any, min_length: int = 1, max_length: int = 100) -> bool:
    """Validate that a field is a string with appropriate length."""
    if not isinstance(value, str):
        return False
    return min_length <= len(value) <= max_length

def validate_timestamp(timestamp: Any) -> bool:
    """Validate that a timestamp is in the correct format."""
    if not isinstance(timestamp, (int, float)):
        return False
    # Check if timestamp is within reasonable range (2000-01-01 to 2100-01-01)
    return 946684800 <= timestamp <= 4102444800

# Data transformation functions
def normalize_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize data by converting fields to standard formats."""
    normalized = data.copy()
    
    # Convert string timestamps to unix timestamps
    if "timestamp" in normalized and isinstance(normalized["timestamp"], str):
        try:
            normalized["timestamp"] = int(time.mktime(time.strptime(normalized["timestamp"], "%Y-%m-%d %H:%M:%S")))
        except ValueError:
            log_message("WARNING", f"Could not parse timestamp: {normalized['timestamp']}")
    
    # Normalize string fields
    for key, value in normalized.items():
        if isinstance(value, str):
            normalized[key] = value.strip().lower()
    
    return normalized

def enrich_data(data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
    """Enrich data with additional context information."""
    enriched = data.copy()
    
    # Add processing metadata
    enriched["processed_at"] = int(time.time())
    enriched["processor_id"] = context.get("processor_id", generate_unique_id())
    
    # Add derived fields
    if "payload" in enriched and isinstance(enriched["payload"], dict):
        payload = enriched["payload"]
        if "latitude" in payload and "longitude" in payload:
            if validate_numeric_field(payload["latitude"]) and validate_numeric_field(payload["longitude"]):
                enriched["geo_hash"] = generate_geo_hash(float(payload["latitude"]), float(payload["longitude"]))
    
    return enriched

def generate_geo_hash(latitude: float, longitude: float, precision: int = 6) -> str:
    """Generate a simple geo hash from latitude and longitude."""
    # This is a simplified version for demonstration
    return f"geo{int(latitude * 1000)}x{int(longitude * 1000)}p{precision}"

def transform_for_storage(data: Dict[str, Any]) -> Dict[str, Any]:
    """Transform data for efficient storage."""
    storage_format = {
        "id": data.get("id", ""),
        "ts": data.get("timestamp", 0),
        "data": json.dumps(data.get("payload", {}))
    }
    
    # Add any derived fields that we want to keep
    for key in ["geo_hash", "processed_at", "processor_id"]:
        if key in data:
            storage_format[key] = data[key]
    
    return storage_format

def transform_for_analytics(data: Dict[str, Any]) -> Dict[str, Any]:
    """Transform data for analytics processing."""
    analytics_format = {
        "event_id": data.get("id", ""),
        "event_time": data.get("timestamp", 0),
        "event_type": determine_event_type(data),
        "metrics": extract_metrics(data),
        "dimensions": extract_dimensions(data)
    }
    
    return analytics_format

def determine_event_type(data: Dict[str, Any]) -> str:
    """Determine the type of event from the data."""
    payload = data.get("payload", {})
    
    if "event_type" in payload:
        return payload["event_type"]
    
    if "action" in payload:
        return payload["action"]
    
    # Try to infer from other fields
    if "purchase_id" in payload:
        return "purchase"
    
    if "view_item_id" in payload:
        return "view"
    
    if "search_query" in payload:
        return "search"
    
    return "unknown"

def extract_metrics(data: Dict[str, Any]) -> Dict[str, float]:
    """Extract numeric metrics from the data."""
    metrics = {}
    payload = data.get("payload", {})
    
    for key, value in payload.items():
        if validate_numeric_field(value):
            metrics[key] = float(value)
    
    return metrics

def extract_dimensions(data: Dict[str, Any]) -> Dict[str, str]:
    """Extract string dimensions from the data."""
    dimensions = {}
    payload = data.get("payload", {})
    
    for key, value in payload.items():
        if isinstance(value, str):
            dimensions[key] = value
    
    # Add derived dimensions
    if "geo_hash" in data:
        dimensions["geo_hash"] = data["geo_hash"]
    
    return dimensions

# Data processing stages
def ingest_data(raw_data: str) -> List[Dict[str, Any]]:
    """Ingest raw data and convert to structured format."""
    try:
        parsed_data = json.loads(raw_data)
        
        if isinstance(parsed_data, dict):
            parsed_data = [parsed_data]
        
        if not isinstance(parsed_data, list):
            log_message("ERROR", "Input data must be a JSON object or array")
            return []
        
        return parsed_data
    except json.JSONDecodeError as e:
        log_message("ERROR", f"Failed to parse JSON: {str(e)}")
        return []

def preprocess_batch(batch: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Preprocess a batch of data records."""
    valid_records = []
    
    for record in batch:
        if validate_input_data(record):
            normalized = normalize_data(record)
            valid_records.append(normalized)
        else:
            log_message("WARNING", f"Skipping invalid record: {record.get('id', 'unknown')}")
    
    return valid_records

def process_record(record: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
    """Process a single data record."""
    # Check cache first
    cache_key = f"record:{record.get('id', '')}"
    cached_result = get_cached_result(cache_key)
    if cached_result:
        log_message("INFO", f"Using cached result for record {record.get('id', '')}")
        return cached_result
    
    # Process the record
    try:
        enriched = enrich_data(record, context)
        processed = apply_business_rules(enriched)
        
        # Cache the result
        cache_result(cache_key, processed)
        
        return processed
    except Exception as e:
        log_message("ERROR", f"Failed to process record {record.get('id', '')}: {str(e)}")
        raise

def apply_business_rules(data: Dict[str, Any]) -> Dict[str, Any]:
    """Apply business rules to the data."""
    result = data.copy()
    payload = result.get("payload", {})
    
    # Apply categorization rules
    if "category" not in payload and "product_name" in payload:
        payload["category"] = categorize_product(payload["product_name"])
    
    # Apply pricing rules
    if "price" in payload and "discount" in payload:
        if validate_numeric_field(payload["price"]) and validate_numeric_field(payload["discount"]):
            price = float(payload["price"])
            discount = float(payload["discount"])
            payload["final_price"] = calculate_final_price(price, discount)
    
    # Apply risk scoring
    result["risk_score"] = calculate_risk_score(result)
    
    # Update the payload
    result["payload"] = payload
    
    return result

def categorize_product(product_name: str) -> str:
    """Categorize a product based on its name."""
    product_name = product_name.lower()
    
    categories = {
        "electronics": ["phone", "laptop", "tablet", "computer", "tv", "camera"],
        "clothing": ["shirt", "pants", "dress", "jacket", "shoes", "hat"],
        "home": ["furniture", "kitchen", "bed", "bath", "decor"],
        "sports": ["fitness", "exercise", "bike", "basketball", "football", "tennis"]
    }
    
    for category, keywords in categories.items():
        for keyword in keywords:
            if keyword in product_name:
                return category
    
    return "other"

def calculate_final_price(price: float, discount: float) -> float:
    """Calculate the final price after applying a discount."""
    if discount > 1.0:
        # Assume discount is a percentage if > 1
        discount = discount / 100.0
    
    if discount < 0.0:
        discount = 0.0
    elif discount > 0.9:
        discount = 0.9  # Cap discount at 90%
    
    return price * (1.0 - discount)

def calculate_risk_score(data: Dict[str, Any]) -> float:
    """Calculate a risk score for the data."""
    score = 0.0
    payload = data.get("payload", {})
    
    # Check for missing fields
    required_fields = ["id", "timestamp", "user_id"]
    for field in required_fields:
        if field not in data and field not in payload:
            score += 0.2
    
    # Check for unusual patterns
    if "ip_address" in payload and payload["ip_address"] in ["127.0.0.1", "0.0.0.0"]:
        score += 0.5
    
    # Check for high-value transactions
    if "price" in payload and validate_numeric_field(payload["price"]):
        price = float(payload["price"])
        if price > 1000:
            score += 0.1
        if price > 10000:
            score += 0.3
    
    # Cap the score at 1.0
    return min(score, 1.0)

def process_batch(batch: List[Dict[str, Any]], context: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Process a batch of records."""
    preprocessed = preprocess_batch(batch)
    results = []
    
    for record in preprocessed:
        try:
            processed = process_record(record, context)
            results.append(processed)
        except Exception as e:
            log_message("ERROR", f"Error processing record: {str(e)}")
            # Continue processing other records
    
    return results

# Storage functions
def prepare_for_storage(processed_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Prepare processed data for storage."""
    storage_records = []
    
    for record in processed_data:
        try:
            storage_record = transform_for_storage(record)
            storage_records.append(storage_record)
        except Exception as e:
            log_message("ERROR", f"Error preparing record for storage: {str(e)}")
    
    return storage_records

def store_data(storage_records: List[Dict[str, Any]], storage_type: str = "file") -> bool:
    """Store data in the specified storage system."""
    if not storage_records:
        log_message("WARNING", "No records to store")
        return True
    
    try:
        if storage_type == "file":
            return store_in_file(storage_records)
        elif storage_type == "database":
            return store_in_database(storage_records)
        else:
            log_message("ERROR", f"Unsupported storage type: {storage_type}")
            return False
    except Exception as e:
        log_message("ERROR", f"Error storing data: {str(e)}")
        return False

def store_in_file(records: List[Dict[str, Any]]) -> bool:
    """Store records in a file (simulated)."""
    log_message("INFO", f"Storing {len(records)} records in file")
    # In a real implementation, this would write to a file
    return True

def store_in_database(records: List[Dict[str, Any]]) -> bool:
    """Store records in a database (simulated)."""
    log_message("INFO", f"Storing {len(records)} records in database")
    # In a real implementation, this would write to a database
    return True

# Analytics functions
def prepare_for_analytics(processed_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Prepare processed data for analytics."""
    analytics_records = []
    
    for record in processed_data:
        try:
            analytics_record = transform_for_analytics(record)
            analytics_records.append(analytics_record)
        except Exception as e:
            log_message("ERROR", f"Error preparing record for analytics: {str(e)}")
    
    return analytics_records

def aggregate_metrics(analytics_records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Aggregate metrics from analytics records."""
    aggregates = {
        "count": len(analytics_records),
        "event_types": {},
        "metrics": {}
    }
    
    for record in analytics_records:
        # Count event types
        event_type = record.get("event_type", "unknown")
        if event_type not in aggregates["event_types"]:
            aggregates["event_types"][event_type] = 0
        aggregates["event_types"][event_type] += 1
        
        # Aggregate metrics
        for metric_name, metric_value in record.get("metrics", {}).items():
            if metric_name not in aggregates["metrics"]:
                aggregates["metrics"][metric_name] = {
                    "sum": 0,
                    "count": 0,
                    "min": float('inf'),
                    "max": float('-inf')
                }
            
            aggregates["metrics"][metric_name]["sum"] += metric_value
            aggregates["metrics"][metric_name]["count"] += 1
            aggregates["metrics"][metric_name]["min"] = min(aggregates["metrics"][metric_name]["min"], metric_value)
            aggregates["metrics"][metric_name]["max"] = max(aggregates["metrics"][metric_name]["max"], metric_value)
    
    # Calculate averages
    for metric_name, metric_data in aggregates["metrics"].items():
        if metric_data["count"] > 0:
            metric_data["avg"] = metric_data["sum"] / metric_data["count"]
        else:
            metric_data["avg"] = 0
    
    return aggregates

def generate_analytics_report(aggregates: Dict[str, Any]) -> str:
    """Generate a human-readable analytics report."""
    report = []
    report.append("=== Analytics Report ===")
    report.append(f"Total records: {aggregates['count']}")
    
    report.append("\nEvent Types:")
    for event_type, count in aggregates["event_types"].items():
        report.append(f"  {event_type}: {count} ({count/aggregates['count']*100:.1f}%)")
    
    report.append("\nMetrics:")
    for metric_name, metric_data in aggregates["metrics"].items():
        report.append(f"  {metric_name}:")
        report.append(f"    Average: {metric_data.get('avg', 0):.2f}")
        report.append(f"    Min: {metric_data.get('min', 0):.2f}")
        report.append(f"    Max: {metric_data.get('max', 0):.2f}")
        report.append(f"    Count: {metric_data.get('count', 0)}")
    
    return "\n".join(report)

# Main processing pipeline
def process_data_pipeline(raw_data: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
    """Run the complete data processing pipeline."""
    if context is None:
        context = {"processor_id": generate_unique_id()}
    
    log_message("INFO", "Starting data processing pipeline")
    
    # Ingest data
    log_message("INFO", "Ingesting data")
    ingested_data = ingest_data(raw_data)
    if not ingested_data:
        log_message("ERROR", "No valid data to process")
        return {"success": False, "error": "No valid data to process"}
    
    # Process data in batches
    log_message("INFO", f"Processing {len(ingested_data)} records")
    batch_size = context.get("batch_size", DEFAULT_BATCH_SIZE)
    all_processed = []
    
    for i in range(0, len(ingested_data), batch_size):
        batch = ingested_data[i:i+batch_size]
        log_message("INFO", f"Processing batch {i//batch_size + 1} ({len(batch)} records)")
        
        processed_batch = process_batch(batch, context)
        all_processed.extend(processed_batch)
    
    # Prepare and store data
    log_message("INFO", "Preparing data for storage")
    storage_records = prepare_for_storage(all_processed)
    
    log_message("INFO", "Storing data")
    storage_success = store_data(storage_records, context.get("storage_type", "file"))
    
    # Prepare and analyze data
    log_message("INFO", "Preparing data for analytics")
    analytics_records = prepare_for_analytics(all_processed)
    
    log_message("INFO", "Aggregating metrics")
    aggregates = aggregate_metrics(analytics_records)
    
    log_message("INFO", "Generating analytics report")
    report = generate_analytics_report(aggregates)
    
    log_message("INFO", "Data processing pipeline completed")
    
    return {
        "success": True,
        "processed_count": len(all_processed),
        "storage_success": storage_success,
        "analytics": aggregates,
        "report": report
    }

# Example usage
def main():
    # Example data
    example_data = json.dumps([
        {
            "id": "event-001",
            "timestamp": int(time.time()),
            "payload": {
                "user_id": "user-123",
                "product_name": "Smartphone XL",
                "price": 799.99,
                "discount": 0.1,
                "action": "purchase"
            }
        },
        {
            "id": "event-002",
            "timestamp": int(time.time()),
            "payload": {
                "user_id": "user-456",
                "product_name": "Running Shoes",
                "price": 129.99,
                "discount": 0.05,
                "action": "view"
            }
        }
    ])
    
    # Process the data
    result = process_data_pipeline(example_data)
    
    # Print the report
    print("\n" + result["report"])

if __name__ == "__main__":
    main()