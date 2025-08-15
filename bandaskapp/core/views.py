from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta

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
        
        context = {
            'dhw_temp': status.get('dhw_temperature', 0),
            'dhw_temp_2': status.get('dhw_temperature_2', 0),  # DHW middle
            'dhw_temp_3': status.get('dhw_temperature_3', 0),  # DHW bottom
            'dhw_temp_low': status.get('dhw_temp_thresholds', {}).get('low', 45),
            'dhw_temp_high': status.get('dhw_temp_thresholds', {}).get('high', 60),
            'furnace_running': status.get('furnace_running', False),
            'control_mode': status.get('control_mode', 'automatic'),
            'dhw_sensor_online': status.get('dhw_sensor_online', False),
            'dhw_sensor_2_online': status.get('dhw_sensor_2_online', False),
            'dhw_sensor_3_online': status.get('dhw_sensor_3_online', False),
            'api_connected': status.get('api_connected', False),
            'last_reading': status.get('last_reading'),
            'recent_logs': recent_logs,
            'error': status.get('error'),
        }
        
        return render(request, 'dashboard.html', context)
        
    except Exception as e:
        return render(request, 'dashboard.html', {
            'error': f'System error: {e}',
            'dhw_temp': 0,
            'dhw_temp_2': 0,
            'dhw_temp_3': 0,
            'furnace_running': False,
            'control_mode': 'unknown',
        })

def api_status(request):
    """API endpoint for status updates"""
    try:
        controller = HardwareController()
        status = controller.get_system_status()
        
        # Format response
        response_data = {
            'dhw_temp': status.get('dhw_temperature', 0),
            'dhw_temp_2': status.get('dhw_temperature_2', 0),  # DHW middle
            'dhw_temp_3': status.get('dhw_temperature_3', 0),  # DHW bottom
            'dhw_temp_low': status.get('dhw_temp_thresholds', {}).get('low', 45),
            'dhw_temp_high': status.get('dhw_temp_thresholds', {}).get('high', 60),
            'furnace_running': status.get('furnace_running', False),
            'control_mode': status.get('control_mode', 'automatic'),
            'dhw_sensor_online': status.get('dhw_sensor_online', False),
            'dhw_sensor_2_online': status.get('dhw_sensor_2_online', False),
            'dhw_sensor_3_online': status.get('dhw_sensor_3_online', False),
            'api_connected': status.get('api_connected', False),
            'timestamp': timezone.now().isoformat(),
            'success': True,
        }
        
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
                    
            elif action == 'sync_relays':
                # Synchronize relay states
                controller.sync_relay_states()
                return JsonResponse({
                    'success': True,
                    'message': 'Relay states synchronized'
                })
                
            elif action == 'update_thresholds':
                # Update temperature thresholds
                try:
                    dhw_low = float(request.POST.get('dhw_low', 45))
                    dhw_high = float(request.POST.get('dhw_high', 60))
                    
                    # Validate thresholds
                    if dhw_low >= dhw_high:
                        return JsonResponse({
                            'success': False,
                            'error': 'Low threshold must be less than high threshold'
                        }, status=400)
                    
                    if dhw_low < 20 or dhw_high > 80:
                        return JsonResponse({
                            'success': False,
                            'error': 'Temperature thresholds must be between 20°C and 80°C'
                        }, status=400)
                    
                    # Update system state
                    system_state = SystemState.load()
                    system_state.dhw_temp_low = dhw_low
                    system_state.dhw_temp_high = dhw_high
                    system_state.save()
                    
                    # Log the change
                    SystemLog.objects.create(
                        level='info',
                        message=f'Temperature thresholds updated: {dhw_low}°C - {dhw_high}°C',
                        component='web_interface'
                    )
                    
                    return JsonResponse({
                        'success': True,
                        'message': f'Temperature thresholds updated to {dhw_low}°C - {dhw_high}°C'
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

def settings(request):
    """Settings view"""
    try:
        system_state = SystemState.load()
        
        context = {
            'system_state': system_state,
        }
        
        return render(request, 'settings.html', context)
        
    except Exception as e:
        return render(request, 'settings.html', {
            'error': f'Error loading settings: {e}',
        })