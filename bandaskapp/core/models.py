from django.db import models
from django.utils import timezone

class TemperatureSensor(models.Model):
    """Model for temperature sensors (DS18B20)"""
    name = models.CharField(max_length=50, help_text="Sensor name (e.g., DHW-1)")
    circuit_id = models.CharField(max_length=20, unique=True, help_text="EVOK circuit ID")
    location = models.CharField(max_length=50, blank=True, help_text="Physical location")
    current_value = models.FloatField(null=True, blank=True, help_text="Current temperature in °C")
    last_reading = models.DateTimeField(null=True, blank=True, help_text="Last successful reading")
    is_lost = models.BooleanField(default=False, help_text="Sensor communication lost")
    is_active = models.BooleanField(default=True, help_text="Sensor is active")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'temperature_sensors'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.current_value}°C)"
    
    @property
    def is_online(self):
        """Check if sensor has recent readings (within 60 seconds)"""
        if not self.last_reading:
            return False
        return (timezone.now() - self.last_reading).total_seconds() < 60

class Relay(models.Model):
    """Model for relay controls"""
    name = models.CharField(max_length=50, help_text="Relay name (e.g., Furnace)")
    circuit_id = models.CharField(max_length=20, unique=True, help_text="EVOK circuit ID")
    purpose = models.CharField(max_length=100, blank=True, help_text="Purpose description")
    current_state = models.BooleanField(default=False, help_text="Current relay state (ON/OFF)")
    expected_state = models.BooleanField(default=False, help_text="Expected relay state")
    last_change = models.DateTimeField(auto_now=True, help_text="Last state change")
    is_active = models.BooleanField(default=True, help_text="Relay is active")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'relays'
        ordering = ['name']
    
    def __str__(self):
        state = "ON" if self.current_state else "OFF"
        return f"{self.name} ({state})"
    
    @property
    def state_mismatch(self):
        """Check if current state doesn't match expected state"""
        return self.current_state != self.expected_state

class SystemState(models.Model):
    """Model for overall system state - singleton pattern"""
    CONTROL_MODES = [
        ('automatic', 'Automatic Mode'),
        ('manual', 'Manual Mode'),
    ]
    
    control_mode = models.CharField(
        max_length=20, 
        choices=CONTROL_MODES, 
        default='automatic',
        help_text="System control mode"
    )
    furnace_running = models.BooleanField(default=False, help_text="Furnace is currently running")
    dhw_temp_low = models.FloatField(default=45.0, help_text="DHW low temperature threshold (°C)")
    dhw_temp_high = models.FloatField(default=60.0, help_text="DHW high temperature threshold (°C)")
    last_update = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'system_state'
    
    def __str__(self):
        return f"System ({self.control_mode})"
    
    def save(self, *args, **kwargs):
        # Ensure only one instance exists (singleton pattern)
        self.pk = 1
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        # Prevent deletion of singleton
        pass
    
    @classmethod
    def load(cls):
        """Load the singleton system state"""
        obj, created = cls.objects.get_or_create(pk=1)
        return obj

class TemperatureLog(models.Model):
    """Model for temperature history logging"""
    sensor = models.ForeignKey(TemperatureSensor, on_delete=models.CASCADE)
    value = models.FloatField(help_text="Temperature value in °C")
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'temperature_logs'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['sensor', '-timestamp']),
        ]
    
    def __str__(self):
        return f"{self.sensor.name}: {self.value}°C at {self.timestamp}"

class SystemLog(models.Model):
    """Model for system event logging"""
    LOG_LEVELS = [
        ('info', 'Info'),
        ('warning', 'Warning'),
        ('error', 'Error'),
    ]
    
    level = models.CharField(max_length=10, choices=LOG_LEVELS, help_text="Log level")
    message = models.TextField(help_text="Log message")
    component = models.CharField(max_length=50, blank=True, help_text="System component")
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'system_logs'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['level', '-timestamp']),
        ]
    
    def __str__(self):
        return f"[{self.level.upper()}] {self.message[:50]}..."