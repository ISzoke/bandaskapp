# BandaskApp - Blind Spots and Edge Cases

## Critical Missing Specifications

### 1. Error Recovery and System Resilience

#### Hardware Communication Failures
- **Missing**: What happens when EVOK API is unreachable?
The API returns actual state of relays. These can be regularly checked and compared with expected state. If the API is unreachable, warning should be dispplayed with time of the last access to indicate the delay of the problem. It may sense to play some alarm sound.
When the API is back, BandaskApp should check the state of HW first and update it acording to the expected state. This should also happen on startup to prevent quick on/off/on. every Relay and Output should have some cool down period SWITCH_COOLDOWN_TIME_FURNACE = 30s and SWITCH_COOLDOWN_TIME_PUMP = 5s
Temperature sensors should have preset expected ranges, and whatever reading outside should be indicated as warning in blinking red and. Nonsense values (<0 and >100) and large jumps (more than 20 degrees per 5s) should be warned also.
Timeout API calls should be warned. This means that display should have some warning log with exclamation. On click, I should see list of warnings with timestamps.


#### Database Connection Issues
- **Missing**: Database corruption or connection loss handling
Database should not be critical. The database should be used just for loging of historical values and for some graph charts data.

### 2. Safety and Emergency Scenarios

#### Emergency Shutdown Procedures
- **Missing**: Complete system shutdown protocols
There should be automatic and manual mode (switch on display). In manual mode, I should be able to switch on/off relays and outputs.


#### Temperature Safety Limits
- **Missing**: Absolute temperature limits and safety checks
see above in HW communication failures

### 3. Data Management and Storage

#### Log Retention and Cleanup
- **Missing**: Data lifecycle management
There should be detailed retention of data for 1 week in database (sqlite). The raw HW data will be written to TSV file. These file will be created per every day. Next day, the previous day tsv is gziped

#### Data Export and Backup
- **Missing**: Data portability and backup procedures
Database can be backed up. But no special treatment is needed

### 4. Network and Communication

#### Network Configuration
- **Missing**: Network setup and troubleshooting
Everything runs on localhost


#### API Rate Limiting
- **Missing**: EVOK API usage limits
There are no limits however I expect to read the API in preset interval. Something between 2s and 10s

### 5. User Interface Edge Cases

#### Touch Interface Failures
- **Missing**: Touch screen malfunction handling
Not needed.

#### Display and Resolution Issues
- **Missing**: Display configuration and troubleshooting
The display will be fixed and oriented in landscape mode. No special treatment is needed

### 6. System Integration Gaps

#### Operating System Dependencies
- **Missing**: OS-specific requirements and limitations
Everything is frozen and when the project will run, image is done to prevent updates and breake of the app due some changes. It is important to let the BandaskApp to run for many years without any human updates

#### Service Dependencies
- **Missing**: External service dependencies
The service should start after evok.service with some delay let say 10s


### 7. Performance and Scalability

#### Memory and Resource Management
- **Missing**: Resource usage limits and monitoring
Not a problem


#### Concurrent Access Handling
- **Missing**: Multiple user access scenarios
Not a problem

### 8. Configuration Management

#### Environment-Specific Configurations
- **Missing**: Different deployment environments
No. Single RPi

#### Dynamic Configuration Updates
- **Missing**: Runtime configuration changes
Not needed


### 9. Testing and Validation Gaps

#### Hardware Testing Procedures
- **Missing**: Real hardware validation procedures
It will be tested with real HW in limited scale


#### Integration Testing Scenarios
- **Missing**: Complete system integration testing
This would be nice with HW simulater

### 10. Security and Access Control

#### Authentication and Authorization
- **Missing**: User access control mechanisms
Not needed


#### Network Security
- **Missing**: Network security configuration
The device will work w/o internet connection. Not needed

