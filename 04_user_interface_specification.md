# BandaskApp - User Interface Specification

## Design Principles

### Touch-First Interface
- **Target Size**: Minimum 44px touch targets for all interactive elements
- **Spacing**: Adequate spacing between elements to prevent accidental touches
- **Feedback**: Visual and haptic feedback for all interactions
- **Orientation**: Portrait mode optimized for 10" display
- **Accessibility**: High contrast colors and large text for readability

### Kiosk Mode Requirements
- **Full Screen**: Application runs in full-screen mode
- **No Scrollbars**: Content fits within viewport
- **Persistent**: Application stays active and visible
- **Override Controls**: Easy access to manual controls
- **Status Visibility**: Clear indication of system state

## Page Layouts

### Main Dashboard (`/`)

#### Header Section
```
┌─────────────────────────────────────────┐
│ BandaskApp                    [Settings]│
├─────────────────────────────────────────┤
│ Operating Mode: [Summer] [Winter] [PVE] │
│ Control Mode: [Automatic] [Manual]      │
└─────────────────────────────────────────┘
```

#### Temperature Display Section
```
┌─────────────────────────────────────────┐
│ Temperature Readings                     │
├─────────────────┬───────────────────────┤
│ DHW (Upper)     │ HHW (Middle)          │
│ 58.2°C          │ 45.1°C                │
│ [Status: OK]    │ [Status: OK]          │
├─────────────────┼───────────────────────┤
│ PVE (Bottom)    │ Target Ranges         │
│ 72.3°C          │ DHW: 45-60°C          │
│ [Status: OK]    │ HHW: 40-50°C          │
└─────────────────┴───────────────────────┘
```

#### System Status Section
```
┌─────────────────────────────────────────┐
│ System Status                           │
├─────────────────┬───────────────────────┤
│ Furnace         │ Heating Pump          │
│ [ON] [OFF]      │ [ON] [OFF]            │
│ Status: Running │ Status: Idle          │
├─────────────────┼───────────────────────┤
│ PVE Heater      │ Heating Demand        │
│ [ON] [OFF]      │ [Active] [Inactive]   │
│ Status: Off     │ Status: Inactive      │
└─────────────────┴───────────────────────┘
```

#### Control Override Section
```
┌─────────────────────────────────────────┐
│ Manual Override Controls                 │
├─────────────────┬───────────────────────┤
│ Furnace         │ Heating Pump          │
│ [Force ON]      │ [Force ON]            │
│ [Force OFF]     │ [Force OFF]           │
│ [Auto Mode]     │ [Auto Mode]           │
├─────────────────┼───────────────────────┤
│ PVE Heater      │ Emergency Stop        │
│ [Force ON]      │ [EMERGENCY STOP]      │
│ [Force OFF]     │ (Red Button)          │
│ [Auto Mode]     │                       │
└─────────────────┴───────────────────────┘
```

#### System Logs Section
```
┌─────────────────────────────────────────┐
│ Recent System Logs                      │
├─────────────────────────────────────────┤
│ 14:32:15 - Furnace started (DHW low)    │
│ 14:30:22 - Temperature reading updated  │
│ 14:28:45 - Heating pump stopped         │
│ 14:25:10 - System mode: Summer          │
└─────────────────────────────────────────┘
```

#### Warning Logs Section
```
┌─────────────────────────────────────────┐
│ ⚠️ Active Warnings (3) [View All]       │
├─────────────────────────────────────────┤
│ 14:35:22 - API Timeout (2s ago)         │
│ 14:30:15 - Sensor DHW-1 out of range    │
│ 14:25:08 - Temperature jump detected    │
└─────────────────────────────────────────┘
```

### Settings Page (`/settings/`)

#### Configuration Section
```
┌─────────────────────────────────────────┐
│ System Configuration                    │
├─────────────────────────────────────────┤
│ Temperature Thresholds                  │
│ DHW Low:  [45.0°C] [Save]              │
│ DHW High: [60.0°C] [Save]              │
│ HHW Low:  [40.0°C] [Save]              │
│ HHW High: [50.0°C] [Save]              │
│ PVE Max:  [80.0°C] [Save]              │
├─────────────────────────────────────────┤
│ Hardware Settings                       │
│ Mode: [Simulator] [Real Hardware]      │
│ EVOK URL: [http://127.0.0.1:8080]      │
│ Update Interval: [10] seconds           │
└─────────────────────────────────────────┘
```

#### Maintenance Section
```
┌─────────────────────────────────────────┐
│ System Maintenance                      │
├─────────────────────────────────────────┤
│ [Clear System Logs]                     │
│ [Clear Temperature Logs]                │
│ [Export System Data]                    │
│ [Restart Application]                   │
│ [Shutdown System]                       │
└─────────────────────────────────────────┘
```

## Bootstrap Components

### Cards
- **Temperature Cards**: Display sensor readings with status indicators
- **Status Cards**: Show system component states
- **Control Cards**: Manual override buttons
- **Log Cards**: System activity display

### Buttons
- **Primary**: Blue buttons for main actions
- **Success**: Green buttons for "ON" states
- **Danger**: Red buttons for "OFF" and emergency actions
- **Warning**: Orange buttons for manual overrides
- **Info**: Blue buttons for information actions

### Alerts
- **Success**: Green alerts for normal operation
- **Warning**: Yellow alerts for temperature warnings
- **Danger**: Red alerts for system errors
- **Info**: Blue alerts for system information
- **Blinking Red**: Critical warnings (sensor failures, API issues)
- **Warning Badge**: Exclamation mark for active warnings

### Progress Bars
- **Temperature Progress**: Visual representation of temperature ranges
- **System Health**: Overall system status indicator

### Badges
- **Status Badges**: ON/OFF indicators
- **Mode Badges**: Operating mode indicators
- **Alert Badges**: Warning and error counts

## Color Scheme

### Primary Colors
- **Primary Blue**: `#007bff` - Main brand color
- **Success Green**: `#28a745` - Normal operation
- **Warning Orange**: `#ffc107` - Caution states
- **Danger Red**: `#dc3545` - Error states
- **Info Blue**: `#17a2b8` - Information

### Background Colors
- **Light Gray**: `#f8f9fa` - Page background
- **White**: `#ffffff` - Card backgrounds
- **Dark Gray**: `#343a40` - Header background

### Text Colors
- **Dark**: `#212529` - Primary text
- **Muted**: `#6c757d` - Secondary text
- **White**: `#ffffff` - Text on dark backgrounds

## Responsive Design

### Breakpoints
- **Extra Small**: < 576px (not used for kiosk)
- **Small**: ≥ 576px (minimum for 10" display)
- **Medium**: ≥ 768px (target for 10" display)
- **Large**: ≥ 992px (maximum for 10" display)

### Grid System
- **12-column grid**: Bootstrap's standard grid
- **Responsive columns**: Adapt to screen size
- **Gutters**: Consistent spacing between elements

## Interactive Elements

### Touch Targets
- **Minimum Size**: 44px × 44px for all buttons
- **Padding**: 12px minimum padding around text
- **Spacing**: 8px minimum between adjacent elements

### Feedback
- **Hover Effects**: Visual feedback on touch
- **Active States**: Pressed state indication
- **Loading States**: Spinner for async operations
- **Success/Error**: Immediate feedback for actions

### Navigation
- **Breadcrumbs**: Clear navigation path
- **Back Buttons**: Easy return to previous page
- **Home Button**: Quick return to dashboard
- **Settings Access**: Always available from header

## Accessibility Features

### Visual Accessibility
- **High Contrast**: Minimum 4.5:1 contrast ratio
- **Large Text**: Minimum 16px font size
- **Clear Icons**: Meaningful iconography
- **Status Indicators**: Color and text status

### Touch Accessibility
- **Large Buttons**: Easy to press accurately
- **Clear Labels**: Descriptive button text
- **Consistent Layout**: Predictable interface
- **Error Prevention**: Confirmation for critical actions

### Screen Reader Support
- **ARIA Labels**: Proper accessibility labels
- **Semantic HTML**: Meaningful structure
- **Alt Text**: Descriptive image alternatives
- **Focus Indicators**: Clear focus states

## JavaScript Functionality

### Real-time Updates
- **AJAX Polling**: 5-10 second intervals
- **WebSocket Support**: For future real-time features
- **Smooth Transitions**: Animated state changes
- **Loading Indicators**: Progress feedback

### User Interactions
- **Form Validation**: Client-side validation
- **Confirmation Dialogs**: Critical action confirmations
- **Toast Notifications**: Success/error messages
- **Modal Dialogs**: Settings and configuration

### Data Visualization
- **Temperature Charts**: Historical data display
- **Status Indicators**: Real-time system state
- **Progress Bars**: Visual progress representation
- **Alert System**: Notification management
