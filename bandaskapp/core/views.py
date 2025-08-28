from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from django.contrib import messages
from django.utils import timezone
from django.conf import settings
from datetime import timedelta
import json

from core.models import TemperatureSensor, Relay, SystemState, SystemLog, TemperatureLog
from hardware.controller import HardwareController

def dashboard(request):
    """Main dashboard view"""
    try:
        # Get hardware controller
        controller = HardwareController()
        
        # Get system status
        status = controller.get_system_status()
        
        # Get recent system logs
        recent_logs = SystemLog.objects.order_by('-timestamp')[:10]
        
        # Get configuration to check which sensors are enabled
        config = settings.BANDASKAPP_CONFIG
        
        # Get system state for winter regime and thresholds
        system_state = SystemState.load()
        
        # Process thermometer configuration generically
        thermometers = []
        for i, thermometer in enumerate(config['THERMOMETERS']):
            # Skip sensors labeled as 'NONE' (not shown in UI)
            if thermometer['label'] == 'NONE':
                continue
                
            thermometers.append({
                'index': i,
                'id': thermometer['id'],
                'label': thermometer['label'],
                'color': thermometer['color'],
                'enabled': True,  # All non-NONE sensors are enabled
                'temp_key': f'temp_{i+1}',
                'online_key': f'sensor_{i+1}_online'
            })
        
        # Build dynamic context based on configuration
        context = {
            'dhw_temp_low': status.get('dhw_temp_thresholds', {}).get('low', 45),
            'dhw_temp_high': status.get('dhw_temp_thresholds', {}).get('high', 60),
            'hhw_temp_low': system_state.hhw_temp_low,
            'hhw_temp_high': system_state.hhw_temp_high,
            'furnace_running': status.get('furnace_running', False),
            'pump_running': status.get('pump_running', False),
            'control_mode': status.get('control_mode', 'automatic'),
            'winter_regime_state': system_state.winter_regime_state,
            'heating_controller_state': status.get('heating_controller_state'),
            'api_connected': status.get('api_connected', False),
            'last_reading': status.get('last_reading'),
            'recent_logs': recent_logs,
            'error': status.get('error'),
            
            # Generic thermometer configuration
            'thermometers': thermometers,
            
            # Hardware circuit IDs for the hardware values card
            'furnace_relay_id': config.get('FURNACE_RELAY_ID', ''),
            'pump_relay_id': config.get('PUMP_RELAY_ID', ''),
            'heating_control_unit_id': config.get('HEATING_CONTROL_UNIT_ID', ''),
            'control_dhw_id': config.get('CONTROL_DHW_ID', ''),
            'control_hhw_id': config.get('CONTROL_HHW_ID', ''),
        }
        
        # Add dynamic temperature and sensor status for each thermometer
        for i, thermometer in enumerate(thermometers):
            temp_key = thermometer['temp_key']
            online_key = thermometer['online_key']
            
            # Get temperature from status (fallback to 0 if not available)
            context[temp_key] = status.get(temp_key, 0)
            context[online_key] = status.get(online_key, False)
        
        return render(request, 'dashboard.html', context)
        
    except Exception as e:
        return render(request, 'dashboard.html', {
            'error': f'System error: {e}',
            'thermometers': [],
            'furnace_running': False,
            'control_mode': 'unknown',
        })

def api_status(request):
    """API endpoint for status updates"""
    try:
        controller = HardwareController()
        status = controller.get_system_status()
        
        # Get configuration to check which sensors are enabled
        config = settings.BANDASKAPP_CONFIG
        
        # Get system state for winter regime and thresholds
        system_state = SystemState.load()
        
        # Format response with generic temperature keys
        response_data = {
            'dhw_temp_low': status.get('dhw_temp_thresholds', {}).get('low', 45),
            'dhw_temp_high': status.get('dhw_temp_thresholds', {}).get('high', 60),
            'hhw_temp_low': system_state.hhw_temp_low,
            'hhw_temp_high': system_state.hhw_temp_high,
            'furnace_running': status.get('furnace_running', False),
            'pump_running': status.get('pump_running', False),
            'control_mode': status.get('control_mode', 'automatic'),
            'winter_regime_state': system_state.winter_regime_state,
            'heating_controller_state': status.get('heating_controller_state'),
            'api_connected': status.get('api_connected', False),
            'timestamp': timezone.now().isoformat(),
            'success': True,
        }
        
        # Add all temperature data generically
        for i, thermometer in enumerate(config['THERMOMETERS']):
            if thermometer['label'] == 'NONE':
                continue
                
            temp_key = f'temp_{i+1}'
            online_key = f'sensor_{i+1}_online'
            
            response_data[temp_key] = status.get(temp_key, 0)
            response_data[online_key] = status.get(online_key, False)
        
        # Keep backward compatibility for existing code
        if 'temp_1' in response_data:
            response_data['dhw_temp'] = response_data['temp_1']
            response_data['dhw_sensor_online'] = response_data['sensor_1_online']
        if 'temp_2' in response_data:
            response_data['dhw_temp_2'] = response_data['temp_2']
            response_data['dhw_sensor_2_online'] = response_data['sensor_2_online']
        if 'temp_3' in response_data:
            response_data['dhw_temp_3'] = response_data['temp_3']
            response_data['dhw_sensor_3_online'] = response_data['sensor_3_online']
        
        if status.get('last_reading'):
            response_data['last_reading'] = status['last_reading'].isoformat()
        
        return JsonResponse(response_data)
        
    except Exception as e:
        return JsonResponse({
            'error': str(e),
            'success': False,
            'timestamp': timezone.now().isoformat(),
        }, status=500)

@method_decorator(csrf_exempt, name='dispatch')
class ControlView(View):
    """Handle control actions"""
    
    def post(self, request):
        try:
            action = request.POST.get('action')
            controller = HardwareController()
            
            if action == 'toggle_mode':
                # Toggle between automatic and manual mode
                system_state = SystemState.load()
                new_mode = 'manual' if system_state.control_mode == 'automatic' else 'automatic'
                system_state.control_mode = new_mode
                system_state.save()
                
                # Log the change
                SystemLog.objects.create(
                    level='info',
                    message=f'Control mode changed to {new_mode}',
                    component='web_interface'
                )
                
                return JsonResponse({
                    'success': True,
                    'message': f'Control mode changed to {new_mode}',
                    'new_mode': new_mode
                })
                
            elif action == 'manual_furnace_on':
                # Manually turn furnace ON
                success = controller.manual_control_furnace(True)
                if success:
                    return JsonResponse({
                        'success': True,
                        'message': 'Furnace turned ON manually'
                    })
                else:
                    return JsonResponse({
                        'success': False,
                        'error': 'Failed to turn furnace ON'
                    }, status=500)
                    
            elif action == 'manual_furnace_off':
                # Manually turn furnace OFF
                success = controller.manual_control_furnace(False)
                if success:
                    return JsonResponse({
                        'success': True,
                        'message': 'Furnace turned OFF manually'
                    })
                else:
                    return JsonResponse({
                        'success': False,
                        'error': 'Failed to turn furnace OFF'
                    }, status=500)
                    
            elif action == 'pump_on':
                # Manually turn pump ON
                success = controller.manual_control_pump(True)
                if success:
                    return JsonResponse({
                        'success': True,
                        'message': 'Pump turned ON manually'
                    })
                else:
                    return JsonResponse({
                        'success': False,
                        'error': 'Failed to turn pump ON'
                    }, status=500)
                    
            elif action == 'pump_off':
                # Manually turn pump OFF
                success = controller.manual_control_pump(False)
                if success:
                    return JsonResponse({
                        'success': True,
                        'message': 'Pump turned OFF manually'
                    })
                else:
                    return JsonResponse({
                        'success': False,
                        'error': 'Failed to turn pump OFF'
                    }, status=500)
                    
            elif action == 'sync_relays':
                # Synchronize relay states
                controller.sync_relay_states()
                return JsonResponse({
                    'success': True,
                    'message': 'Relay states synchronized'
                })
                
            elif action == 'cycle_winter_regime':
                # Cycle through winter regime states
                system_state = SystemState.load()
                current_state = system_state.winter_regime_state
                
                # Cycle: off -> automatic -> on -> off
                if current_state == 'off':
                    new_state = 'automatic'
                elif current_state == 'automatic':
                    new_state = 'on'
                else:  # 'on'
                    new_state = 'off'
                
                system_state.winter_regime_state = new_state
                system_state.save()
                
                # Log the change
                SystemLog.objects.create(
                    level='info',
                    message=f'Winter regime state changed to {new_state}',
                    component='web_interface'
                )
                
                return JsonResponse({
                    'success': True,
                    'message': f'Winter regime state changed to {new_state}',
                    'new_state': new_state
                })
                
            elif action == 'update_thresholds':
                # Update temperature thresholds
                try:
                    dhw_low = float(request.POST.get('dhw_low', 45))
                    dhw_high = float(request.POST.get('dhw_high', 60))
                    hhw_low = float(request.POST.get('hhw_low', 45))
                    hhw_high = float(request.POST.get('hhw_high', 60))
                    
                    # Validate DHW thresholds
                    if dhw_low >= dhw_high:
                        return JsonResponse({
                            'success': False,
                            'error': 'DHW low threshold must be less than high threshold'
                        }, status=400)
                    
                    # Validate HHW thresholds
                    if hhw_low >= hhw_high:
                        return JsonResponse({
                            'success': False,
                            'error': 'HHW low threshold must be less than high threshold'
                        }, status=400)
                    
                    if dhw_low < 20 or dhw_high > 80 or hhw_low < 20 or hhw_high > 80:
                        return JsonResponse({
                            'success': False,
                            'error': 'Temperature thresholds must be between 20°C and 80°C'
                        }, status=400)
                    
                    # Update system state
                    system_state = SystemState.load()
                    system_state.dhw_temp_low = dhw_low
                    system_state.dhw_temp_high = dhw_high
                    system_state.hhw_temp_low = hhw_low
                    system_state.hhw_temp_high = hhw_high
                    system_state.save()
                    
                    # Log the change
                    SystemLog.objects.create(
                        level='info',
                        message=f'Temperature thresholds updated: DHW {dhw_low}°C-{dhw_high}°C, HHW {hhw_low}°C-{hhw_high}°C',
                        component='web_interface'
                    )
                    
                    return JsonResponse({
                        'success': True,
                        'message': f'Temperature thresholds updated: DHW {dhw_low}°C-{dhw_high}°C, HHW {hhw_low}°C-{hhw_high}°C'
                    })
                    
                except ValueError:
                    return JsonResponse({
                        'success': False,
                        'error': 'Invalid temperature values'
                    }, status=400)
            
            else:
                return JsonResponse({
                    'success': False,
                    'error': f'Unknown action: {action}'
                }, status=400)
                
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)

def logs(request):
    """System logs view"""
    try:
        # Get log level filter
        level_filter = request.GET.get('level', 'all')
        
        # Build query
        logs_query = SystemLog.objects.all()
        if level_filter != 'all':
            logs_query = logs_query.filter(level=level_filter)
        
        # Get recent logs (last 100)
        recent_logs = logs_query.order_by('-timestamp')[:100]
        
        context = {
            'logs': recent_logs,
            'level_filter': level_filter,
            'log_levels': ['all', 'info', 'warning', 'error'],
        }
        
        return render(request, 'logs.html', context)
        
    except Exception as e:
        return render(request, 'logs.html', {
            'error': f'Error loading logs: {e}',
            'logs': [],
        })

def settings_view(request):
    """Settings view"""
    try:
        system_state = SystemState.load()
        
        # Get hardware controller for current status
        controller = HardwareController()
        status = controller.get_system_status()
        
        # Get configuration for hardware circuit IDs
        config = settings.BANDASKAPP_CONFIG
        
        # Process thermometer configuration
        thermometers = []
        for i, thermometer in enumerate(config['THERMOMETERS']):
            thermometers.append({
                'index': i,
                'id': thermometer['id'],
                'label': thermometer['label'],
                'color': thermometer['color'],
                'enabled': thermometer['id'] != 'NONE',
                'temp_key': f'dhw_temp_{i+1}' if i < 3 else f'dhw_temp_{i+1}',
                'online_key': f'dhw_sensor_{i+1}_online' if i < 3 else f'dhw_sensor_{i+1}_online'
            })
        
        context = {
            'system_state': system_state,
            # Add hardware status for the hardware values card
            'dhw_temp': status.get('dhw_temperature', 0),
            'dhw_temp_2': status.get('dhw_temperature_2', 0),
            'dhw_temp_3': status.get('dhw_temperature_3', 0),
            'furnace_running': status.get('furnace_running', False),
            'pump_running': status.get('pump_running', False),
            'heating_controller_state': status.get('heating_controller_state'),
            'dhw_sensor_online': status.get('dhw_sensor_online', False),
            'dhw_sensor_2_online': status.get('dhw_sensor_2_online', False),
            'dhw_sensor_3_online': status.get('dhw_sensor_3_online', False),
            'api_connected': status.get('api_connected', False),
            'thermometers': thermometers,
            # Add hardware circuit IDs
            'furnace_relay_id': config['FURNACE_RELAY_ID'],
            'pump_relay_id': config['PUMP_RELAY_ID'],
            'heating_control_unit_id': config['HEATING_CONTROL_UNIT_ID'],
            'control_dhw_id': config['CONTROL_DHW_ID'],
            'control_hhw_id': config['CONTROL_HHW_ID'],
        }
        
        return render(request, 'settings.html', context)
        
    except Exception as e:
        return render(request, 'settings.html', {
            'error': f'Error loading settings: {e}',
        })


@csrf_exempt
def settings_api(request):
    """Settings API endpoint for handling POST requests"""
    if request.method != 'POST':
        return JsonResponse({
            'success': False,
            'error': 'Only POST method is allowed'
        }, status=405)
    
    try:
        data = json.loads(request.body)
        action = data.get('action')
        
        if action == 'clear_database_history':
            # Clear all system logs
            deleted_logs_count = SystemLog.objects.all().delete()[0]
            
            # Log the action
            SystemLog.objects.create(
                level='info',
                message=f'Database history cleared by user. Deleted {deleted_logs_count} log entries.',
                component='web_interface'
            )
            
            return JsonResponse({
                'success': True,
                'message': f'Database history cleared successfully. Deleted {deleted_logs_count} log entries.',
                'deleted_count': deleted_logs_count
            })
        
        else:
            return JsonResponse({
                'success': False,
                'error': f'Unknown action: {action}'
            }, status=400)
            
    except json.JSONDecodeError as e:
        return JsonResponse({
            'success': False,
            'error': f'Invalid JSON data: {str(e)}'
        }, status=400)
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)