"""
Example demonstrating how to use the TTLCache for caching validation results.
This is intended as documentation/example for developers implementing task 6.
"""

from src.utils.cache import TTLCache
from src.validators.validation_engine import ValidationEngine
from src.models.models import Movimiento
import hashlib
import json

# Create a cache for validation results
# In a real implementation, this might be configured via environment variables
validation_result_cache = TTLCache(maxsize=512, ttl=3600)  # 512 items, 1 hour TTL

def cache_key_from_movimiento(movimiento: Movimiento) -> str:
    """
    Generate a cache key from a Movimiento object.
    We serialize the essential data that affects validation results.
    """
    # Create a dictionary with the data that affects validation
    cache_data = {
        'fecha': movimiento.fecha,
        'numero': movimiento.numero,
        'total': movimiento.total,
        'cancelacion': movimiento.cancelacion,
        'descuento_total': movimiento.descuento_total,
        'recargo_total': movimiento.recargo_total,
        'codigo_moneda': movimiento.codigo_moneda,
        'cotizacion': movimiento.cotizacion,
        # For detalles and pagos, we need to serialize their data
        'detalles': sorted([str(sorted(d.data.items())) for d in movimiento.detalles]),
        'pagos': sorted([str(sorted(p.data.items())) for p in movimiento.pagos])
    }

    # Convert to JSON string and hash for a fixed-length key
    json_str = json.dumps(cache_data, sort_keys=True)
    return hashlib.md5(json_str.encode()).hexdigest()

def validar_movimiento_com_cache(movimiento: Movimiento) -> 'ValidationResult':
    """
    Validate a Movimiento using caching to avoid re-validation of identical movements.

    Args:
        movimiento: The Movimiento to validate

    Returns:
        ValidationResult: The validation result (cached or newly computed)
    """
    # Generate cache key
    cache_key = cache_key_from_movimiento(movimiento)

    # Try to get from cache first
    cached_result = validation_result_cache.get(cache_key)
    if cached_result is not None:
        # Return a copy to prevent accidental modification of cached object
        # In practice, ValidationResult should be immutable or we'd return a copy
        return cached_result

    # Not in cache, compute the validation
    engine = ValidationEngine()
    result = engine.validar_movimiento(movimiento)

    # Store in cache for future use
    validation_result_cache.set(cache_key, result)

    return result

def get_cache_statistics():
    """Get statistics about the validation cache."""
    return validation_result_cache.stats()

# Example usage:
if __name__ == "__main__":
    # This is just an example of how it would be used
    # In practice, this would be called from the validation service

    # Create a sample movimiento (this would come from your parsers)
    # movimiento = Movimiento(...)
    #
    # # Validate with caching
    # result = validar_movimiento_com_cache(movimiento)
    #
    # # Check cache stats
    # stats = get_cache_statistics()
    # print(f"Cache hit rate: {stats['hit_rate']:.2%}")
    pass