# Mini-Graph AJAX Update Implementation Guide

## 🎯 **Objective**
Fix the issue where mini-graphs stop receiving new temperature data when switching between tabs. The data persistence is working, but real-time updates stop.

## 🔍 **Current Problem Analysis**
- ✅ **Data persistence**: Mini-graph data is stored in localStorage and survives tab switches
- ❌ **Real-time updates**: New temperature data stops arriving when dashboard tab is inactive
- 🔄 **Root cause**: `updateStatus()` function only runs when dashboard tab is visible
- 📱 **Impact**: Users see stale data when returning to dashboard tab

## 🏗️ **Current Architecture**
```
Dashboard Tab Active:
Hardware → Django API → updateStatus() → Mini-graphs update ✅

Dashboard Tab Inactive:
Hardware → Django API → ❌ No updateStatus() → Mini-graphs stale ❌
```

## 🚀 **Solution: Enhanced AJAX Polling**

### **Approach Overview**
Implement continuous AJAX polling that works regardless of tab visibility, ensuring mini-graphs always receive fresh data.

### **Key Changes Required**

#### **1. Frontend: Enhanced updateStatus() Function**
**File**: `bandaskapp/templates/base.html`
**Location**: Around line 450-500 (in the `<script>` section)

**What to modify**:
- Add `visibilitychange` event listener to detect tab visibility
- Implement background polling when tab is hidden
- Ensure `updateStatus()` continues running in background
- Add tab visibility state management

**What NOT to touch**:
- ❌ Don't modify the existing `updateStatus()` logic
- ❌ Don't change the mini-graph data handling
- ❌ Don't modify localStorage persistence
- ❌ Don't change the 5-second update interval

#### **2. Frontend: Tab Visibility Management**
**File**: `bandaskapp/templates/base.html`
**Location**: After the existing `updateStatus()` function

**What to add**:
- `document.visibilityState` detection
- Background polling logic
- Tab focus/blur event handlers
- Polling state management

#### **3. Frontend: Enhanced Event Listeners**
**File**: `bandaskapp/templates/base.html`
**Location**: In the `DOMContentLoaded` event listener

**What to add**:
- `visibilitychange` event listener
- `focus` and `blur` event listeners
- `beforeunload` event listener for cleanup

## 📝 **Detailed Implementation Steps**

### **Step 1: Add Tab Visibility Detection**
```javascript
// Add this after the existing updateStatus() function
let isTabVisible = true;
let backgroundPollingInterval = null;

// Detect tab visibility changes
document.addEventListener('visibilitychange', function() {
    isTabVisible = !document.hidden;
    console.log(`Tab visibility changed: ${isTabVisible ? 'visible' : 'hidden'}`);
    
    if (isTabVisible) {
        // Tab became visible - resume normal polling
        startNormalPolling();
    } else {
        // Tab became hidden - start background polling
        startBackgroundPolling();
    }
});
```

### **Step 2: Implement Background Polling**
```javascript
function startBackgroundPolling() {
    console.log('Starting background polling for mini-graphs');
    
    // Clear normal polling interval
    if (window.statusUpdateInterval) {
        clearInterval(window.statusUpdateInterval);
        window.statusUpdateInterval = null;
    }
    
    // Start background polling (same 5-second interval)
    backgroundPollingInterval = setInterval(function() {
        // Call updateStatus() even when tab is hidden
        updateStatus();
    }, 5000);
}

function startNormalPolling() {
    console.log('Resuming normal polling for mini-graphs');
    
    // Clear background polling
    if (backgroundPollingInterval) {
        clearInterval(backgroundPollingInterval);
        backgroundPollingInterval = null;
    }
    
    // Resume normal polling
    if (!window.statusUpdateInterval) {
        window.statusUpdateInterval = setInterval(updateStatus, 5000);
    }
}
```

### **Step 3: Add Tab Focus/Blur Handlers**
```javascript
// Handle tab focus/blur events
window.addEventListener('focus', function() {
    console.log('Tab focused - resuming normal polling');
    startNormalPolling();
});

window.addEventListener('blur', function() {
    console.log('Tab blurred - switching to background polling');
    startBackgroundPolling();
});
```

### **Step 4: Add Cleanup on Page Unload**
```javascript
// Cleanup on page unload
window.addEventListener('beforeunload', function() {
    console.log('Page unloading - cleaning up intervals');
    
    if (window.statusUpdateInterval) {
        clearInterval(window.statusUpdateInterval);
    }
    if (backgroundPollingInterval) {
        clearInterval(backgroundPollingInterval);
    }
});
```

### **Step 5: Initialize Polling State**
```javascript
// In the DOMContentLoaded event listener, after existing code
document.addEventListener('DOMContentLoaded', function() {
    // ... existing code ...
    
    // Initialize polling based on current tab state
    if (document.visibilityState === 'visible') {
        startNormalPolling();
    } else {
        startBackgroundPolling();
    }
    
    console.log('Mini-graph AJAX polling initialized');
});
```

## 🚫 **What NOT to Touch (Critical)**

### **1. Mini-Graph Data Handling**
- ❌ **Don't modify**: `miniGraphData` object structure
- ❌ **Don't change**: `createMiniGraph()` function
- ❌ **Don't alter**: `updateData()` function in mini-graphs
- ❌ **Don't touch**: `localStorage` persistence logic

### **2. Existing API Endpoints**
- ❌ **Don't modify**: `/api/status/` endpoint
- ❌ **Don't change**: `updateStatus()` function logic
- ❌ **Don't alter**: Data parsing and assignment
- ❌ **Don't touch**: Error handling in API calls

### **3. Mini-Graph Rendering**
- ❌ **Don't modify**: Canvas drawing functions
- ❌ **Don't change**: Zoom functionality
- ❌ **Don't alter**: Touch/click event handlers
- ❌ **Don't touch**: Chart styling and colors

### **4. localStorage Management**
- ❌ **Don't modify**: `saveMiniGraphData()` function
- ❌ **Don't change**: `loadMiniGraphData()` function
- ❌ **Don't alter**: Data serialization/deserialization
- ❌ **Don't touch**: Auto-save timing (30 seconds)

## 🔧 **Testing Strategy**

### **Test Case 1: Tab Switching**
1. Open dashboard with mini-graphs showing data
2. Switch to another tab (Logs, Settings)
3. Wait 10-15 seconds
4. Return to dashboard
5. **Expected**: Mini-graphs show updated data, not stale data

### **Test Case 2: Background Updates**
1. Open dashboard
2. Switch to another tab
3. Monitor browser network tab
4. **Expected**: API calls to `/api/status/` continue every 5 seconds

### **Test Case 3: Data Persistence**
1. Fill mini-graphs with data
2. Switch tabs multiple times
3. Return to dashboard
4. **Expected**: All historical data preserved, new data continues

## 📊 **Expected Results**

### **Before Fix**
- Mini-graphs stop updating when tab is inactive
- Data becomes stale after tab switch
- No API calls when dashboard is hidden

### **After Fix**
- Mini-graphs continue updating in background
- Fresh data available immediately on tab return
- Continuous API polling regardless of tab state
- No data loss or interruption

## 🚨 **Potential Issues & Mitigation**

### **1. Memory Leaks**
- **Risk**: Multiple intervals running simultaneously
- **Mitigation**: Always clear previous interval before starting new one

### **2. Excessive API Calls**
- **Risk**: Background polling when not needed
- **Mitigation**: Only poll when mini-graphs exist and need updates

### **3. Browser Resource Usage**
- **Risk**: Background JavaScript execution
- **Mitigation**: Use efficient polling, avoid heavy computations

## 📋 **Implementation Checklist**

- [ ] Add tab visibility detection
- [ ] Implement background polling function
- [ ] Add tab focus/blur handlers
- [ ] Add cleanup on page unload
- [ ] Initialize polling state on page load
- [ ] Test tab switching functionality
- [ ] Verify data persistence
- [ ] Check browser console for errors
- [ ] Validate API call frequency
- [ ] Test with multiple tabs open

## 🎯 **Success Criteria**

1. **Mini-graphs continue updating** when dashboard tab is inactive
2. **No data loss** occurs during tab switches
3. **API calls continue** at 5-second intervals regardless of tab state
4. **Smooth user experience** when returning to dashboard
5. **No console errors** or JavaScript exceptions
6. **Efficient resource usage** without excessive API calls

## 🔄 **Next Steps After Implementation**

1. **Test thoroughly** with different tab switching scenarios
2. **Monitor performance** and API call frequency
3. **Consider WebSocket upgrade** for production use
4. **Document any edge cases** discovered during testing
5. **Plan for mobile device** compatibility testing

---

**File Created**: `10_update_ajax_for_minigraphs.md`
**Purpose**: Implementation guide for mini-graph AJAX update fix
**Complexity**: 3/10 (Simple to implement)
**Estimated Time**: 2-3 hours
**Risk Level**: Low (minimal changes to existing code)
