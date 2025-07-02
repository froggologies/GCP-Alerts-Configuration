# Enhanced Alert Descriptions

## Compute Engine Alerts

### VM instance - High CPU utilization
**Alert Description:** Monitors CPU utilization across GCE VM instances and triggers when CPU usage exceeds 80% for 5 consecutive minutes or more.

**Possible Causes:**
- High application workload or traffic spikes
- Resource-intensive processes running on the VM
- Insufficient VM sizing for current workload
- Malware or unauthorized processes consuming CPU
- Memory leaks causing excessive CPU usage

**Recommended Actions:**
- Investigate running processes using top/htop commands
- Scale up VM instance size or add more instances
- Optimize application code for better CPU efficiency
- Implement load balancing to distribute traffic
- Monitor application logs for errors or performance issues

### VM instance - High disk utilization
**Alert Description:** Monitors disk utilization on GCE VMs and alerts when disk usage rises above 95% for 5 minutes or more. Requires Ops Agent installation for metric collection.

**Possible Causes:**
- Log files growing excessively large
- Temporary files not being cleaned up
- Database files expanding rapidly
- Application data accumulation
- Insufficient disk space provisioning

**Recommended Actions:**
- Clean up temporary files and old logs
- Implement log rotation policies
- Resize disk or add additional storage
- Archive old data to cheaper storage tiers
- Set up automated cleanup scripts
- Monitor disk growth patterns to predict future needs

### VM instance - Host error log detected
**Alert Description:** Monitors system event logs for host-level errors on GCE VMs and notifies when host errors occur, with notifications limited to once per hour.

**Possible Causes:**
- Hardware failures or degradation
- Host system crashes or reboots
- Network connectivity issues
- Storage subsystem failures
- Hypervisor-level problems

**Recommended Actions:**
- Check VM health status in Google Cloud Console
- Review system logs for detailed error information
- Consider migrating VM to different host if persistent
- Contact Google Cloud Support for hardware-related issues
- Implement redundancy and failover mechanisms

### VM instance - High memory utilization
**Alert Description:** Monitors memory usage on GCE VMs and triggers when memory utilization exceeds 90% for 5 consecutive minutes. Requires Ops Agent installation.

**Possible Causes:**
- Memory leaks in applications
- Insufficient RAM for current workload
- Too many concurrent processes
- Large datasets loaded into memory
- Caching systems consuming excessive memory

**Recommended Actions:**
- Identify memory-intensive processes using tools like ps or htop
- Restart applications with memory leaks
- Upgrade to VM with more RAM
- Optimize application memory usage
- Implement memory monitoring and alerting
- Consider using swap space as temporary solution

## Interconnect Alerts

### High interconnect egress
**Alert Description:** Triggers when egress bytes per second exceed 70% of an interconnect VLAN attachment's capacity, helping determine when additional capacity is needed.

**Possible Causes:**
- Increased data transfer from cloud to on-premises
- Large file transfers or backups
- Application traffic growth
- Batch processing jobs
- Network optimization changes

**Recommended Actions:**
- Provision additional interconnect capacity
- Create additional VLAN attachments
- Schedule large transfers during off-peak hours
- Implement traffic shaping and QoS policies
- Monitor traffic patterns to predict capacity needs

### High interconnect ingress
**Alert Description:** Alerts when ingress bytes per second exceed 70% of an interconnect VLAN attachment's capacity, indicating potential need for capacity expansion.

**Possible Causes:**
- Increased data uploads from on-premises to cloud
- Migration activities
- Real-time data streaming
- Backup operations
- Application traffic spikes

**Recommended Actions:**
- Add more interconnect bandwidth
- Create additional VLAN attachments for load distribution
- Optimize data transfer schedules
- Implement data compression where possible
- Review and optimize network routing

## VPN Alerts

### High VPN tunnel bps
**Alert Description:** Alerts when combined ingress and egress bytes exceed 50% of the 3-Gbps (375 MBps) limit for a VPN tunnel.

**Possible Causes:**
- Increased application traffic
- Large file transfers
- Backup operations over VPN
- Video conferencing or streaming
- Database replication traffic

**Recommended Actions:**
- Provision additional VPN tunnels
- Implement load balancing across multiple tunnels
- Schedule large transfers during off-peak hours
- Consider upgrading to Cloud Interconnect for higher bandwidth
- Optimize application protocols for better efficiency

### High VPN tunnel pps
**Alert Description:** Triggers when combined ingress and egress packet rate exceeds 50% of the 250,000 pps recommended limit for a VPN tunnel.

**Possible Causes:**
- High-frequency transactional applications
- Gaming or real-time applications
- IoT device communications
- Monitoring and telemetry data
- Small packet applications

**Recommended Actions:**
- Deploy additional VPN tunnels
- Implement packet aggregation where possible
- Optimize application protocols
- Consider Cloud Interconnect for lower latency
- Review traffic patterns and optimize routing

## Cloud Router Alerts

### Router instance unhealthy
**Alert Description:** Indicates Cloud Router is offline, causing complete routing impact and network connectivity loss.

**Possible Causes:**
- Hardware or software failures
- Configuration errors
- Network connectivity issues
- Resource exhaustion
- Google Cloud service outages

**Recommended Actions:**
- Check Cloud Router status in Google Cloud Console
- Verify router configuration
- Implement redundant routers for high availability
- Contact Google Cloud Support immediately
- Review recent configuration changes

### All BGP sessions down - Per peer
**Alert Description:** Triggers when all BGP sessions are down, isolating the Cloud Router from connected networks and preventing route exchange.

**Possible Causes:**
- Network connectivity issues
- BGP configuration errors
- Peer router failures
- Authentication problems
- Firewall blocking BGP traffic

**Recommended Actions:**
- Verify BGP peer configurations
- Check network connectivity to peers
- Review firewall rules for BGP traffic (port 179)
- Validate authentication credentials
- Implement redundant BGP sessions
- Contact network administrators for peer-side issues

## Cloud Data Fusion Alerts

### Failed pipelines
**Alert Description:** Triggers when Data Fusion pipeline execution fails, enabling prompt identification and resolution of pipeline failures to maintain data processing continuity.

**Possible Causes:**
- Data source connectivity issues
- Invalid or corrupted input data
- Insufficient resources or permissions
- Plugin or transformation errors
- Destination system failures

**Recommended Actions:**
- Review pipeline execution logs
- Validate data source connectivity and permissions
- Check input data quality and format
- Verify destination system availability
- Restart failed pipeline runs
- Implement data validation and error handling

### Data Fusion service unhealthy
**Alert Description:** Detects when any Data Fusion service becomes unreachable, indicating potential service availability issues.

**Possible Causes:**
- Service outages or maintenance
- Network connectivity problems
- Resource exhaustion
- Configuration errors
- Google Cloud service issues

**Recommended Actions:**
- Check Data Fusion service status
- Verify network connectivity
- Review service logs for errors
- Restart Data Fusion services if needed
- Contact Google Cloud Support for persistent issues
- Implement health checks and monitoring

## Dataproc Alerts

### No running jobs for 1 hour
**Alert Description:** Indicates cluster has been idle for one hour with no active jobs, potentially representing underutilized resources.

**Possible Causes:**
- Job scheduling gaps
- Completed batch processing
- Application or workflow issues
- Resource over-provisioning
- Planned maintenance windows

**Recommended Actions:**
- Review job scheduling and workflow
- Consider auto-scaling or cluster shutdown policies
- Optimize resource allocation
- Implement just-in-time cluster provisioning
- Review cost optimization opportunities

### Any CREATE_CLUSTER operation took more than 20 minutes
**Alert Description:** Alerts when cluster creation exceeds 20 minutes, indicating potential provisioning issues or resource constraints.

**Possible Causes:**
- Resource availability constraints
- Large cluster configurations
- Image preparation delays
- Network or storage issues
- Google Cloud service delays

**Recommended Actions:**
- Review cluster configuration for optimization
- Consider smaller initial cluster sizes with auto-scaling
- Check regional resource availability
- Use preemptible instances where appropriate
- Monitor cluster creation patterns

### YARN pending memory above 0 GB for 10 minutes
**Alert Description:** Triggers when pending memory in cluster exceeds 0 GB for 10 minutes, indicating resource contention.

**Possible Causes:**
- Insufficient cluster memory resources
- Large job memory requirements
- Memory leaks in applications
- Poor resource allocation configuration
- Concurrent job competition

**Recommended Actions:**
- Scale up cluster memory capacity
- Optimize job memory allocation
- Review and tune YARN configuration
- Implement job scheduling policies
- Monitor application memory usage patterns

### HDFS capacity less than 100 GB
**Alert Description:** Alerts when HDFS available capacity falls below 100 GB threshold, indicating potential storage exhaustion.

**Possible Causes:**
- Data growth exceeding capacity planning
- Large intermediate file generation
- Inefficient data compression
- Lack of data lifecycle management
- Temporary file accumulation

**Recommended Actions:**
- Add more storage capacity to cluster
- Implement data archival policies
- Enable data compression
- Clean up temporary and intermediate files
- Monitor data growth trends

### Running HDFS data nodes less than 2 for 5 minutes
**Alert Description:** Triggers when fewer than 2 HDFS data nodes are running for over 5 minutes, risking data availability and fault tolerance.

**Possible Causes:**
- Node failures or crashes
- Network connectivity issues
- Resource exhaustion on nodes
- Configuration problems
- Maintenance activities

**Recommended Actions:**
- Investigate failed node status and logs
- Restart failed data nodes
- Check network connectivity between nodes
- Verify HDFS configuration
- Ensure minimum replication factor is maintained
- Consider adding more data nodes for redundancy

## Dataproc Jobs Alerts

### Job duration in PENDING status for 10 minutes
**Alert Description:** Alerts when jobs remain in PENDING status for 10 minutes, indicating potential scheduling or resource issues.

**Possible Causes:**
- Insufficient cluster resources
- Job queue congestion
- Resource allocation conflicts
- Configuration errors
- Dependency issues

**Recommended Actions:**
- Review cluster resource availability
- Optimize job resource requirements
- Implement job prioritization
- Check for configuration errors
- Scale cluster resources if needed

### Any job in RUNNING status for 10 hours
**Alert Description:** Triggers when jobs run for more than 10 hours, potentially indicating stuck or inefficient processes.

**Possible Causes:**
- Inefficient job logic or algorithms
- Large dataset processing
- Resource bottlenecks
- Stuck or infinite loops
- Poor job optimization

**Recommended Actions:**
- Review job progress and logs
- Optimize job algorithms and logic
- Implement job timeout mechanisms
- Monitor resource utilization during execution
- Consider breaking large jobs into smaller tasks

## Cloud Composer Alerts

### Composer environment unhealthy
**Alert Description:** Fires when overall Cloud Composer environment health is unhealthy due to failures in scheduler, web server, database, or other components.

**Possible Causes:**
- Resource exhaustion (CPU, memory, disk)
- Component failures or crashes
- Configuration errors
- Network connectivity issues
- Dependency conflicts

**Recommended Actions:**
- Check individual component health status
- Review Airflow UI and Cloud Logging for details
- Restart unhealthy components
- Scale environment resources if needed
- Verify network and firewall configurations

### Composer scheduler unhealthy
**Alert Description:** Indicates Airflow scheduler is not functioning properly, potentially affecting DAG runs and task scheduling.

**Possible Causes:**
- Scheduler process crashes
- Resource constraints
- Database connectivity issues
- Configuration errors
- Python dependency conflicts

**Recommended Actions:**
- Check scheduler logs in Airflow UI
- Restart scheduler component
- Verify database connectivity
- Review DAG code for errors
- Monitor resource utilization

### Composer web server unhealthy
**Alert Description:** Web server is unreachable or unresponsive, preventing access to Airflow UI.

**Possible Causes:**
- Web server process failures
- Resource exhaustion
- Network connectivity issues
- SSL certificate problems
- Configuration errors

**Recommended Actions:**
- Check web server logs
- Restart web server component
- Verify network connectivity and firewall rules
- Review SSL certificate status
- Monitor VM resource utilization

### Composer database unhealthy
**Alert Description:** The underlying Airflow database is unhealthy, potentially breaking task status updates and core functionality.

**Possible Causes:**
- Database connectivity issues
- Resource exhaustion (CPU, memory, disk)
- Database corruption
- Connection pool exhaustion
- Storage issues

**Recommended Actions:**
- Check database metrics and logs
- Verify database connectivity
- Monitor database resource utilization
- Review connection pool settings
- Consider database maintenance or scaling

### Worker pod restarts - Unhealthy workers
**Alert Description:** Indicates frequent worker pod restarts or unhealthy workers, affecting task execution capability.

**Possible Causes:**
- Resource constraints on worker pods
- Application errors causing crashes
- Node failures or instability
- Image or dependency issues
- Configuration problems

**Recommended Actions:**
- Check worker pod logs and events
- Review resource allocation for workers
- Verify node health and stability
- Update worker image or dependencies
- Scale worker pool if needed

### DAG run failures
**Alert Description:** Monitors and alerts on increased count of failed DAG runs for specific DAGs or overall environment.

**Possible Causes:**
- Code errors in DAG tasks
- External dependency failures
- Resource constraints
- Data quality issues
- Configuration problems

**Recommended Actions:**
- Review DAG run logs for error details
- Fix code errors in failing tasks
- Verify external system availability
- Check data quality and availability
- Implement retry mechanisms and error handling

### Task failures
**Alert Description:** Provides granular insight into specific task failures within DAGs.

**Possible Causes:**
- Task code errors or exceptions
- External service failures
- Data processing issues
- Resource limitations
- Timeout conditions

**Recommended Actions:**
- Examine task logs for specific errors
- Debug and fix task code issues
- Verify external dependencies
- Optimize task resource allocation
- Implement proper error handling and retries

## Storage Transfer Service Alerts

### Agent lost connection
**Alert Description:** On-premises source or destination agent is completely unreachable by Storage Transfer Service, causing all transfers using this pool to fail.

**Possible Causes:**
- Network connectivity issues
- Agent process failures or crashes
- Firewall blocking communication
- Authentication or certificate problems
- Resource exhaustion on agent host

**Recommended Actions:**
- Check agent host network connectivity
- Restart Storage Transfer Service agent
- Verify firewall rules and network configuration
- Validate authentication credentials and certificates
- Monitor agent host resources (CPU, memory, disk)
- Review agent logs for detailed error information

### Transfer errors found
**Alert Description:** Indicates potential issues with source data, permissions, network, or destination that may slow down transfers or indicate underlying problems.

**Possible Causes:**
- File permission issues
- Network connectivity problems
- Storage quota limitations
- Data corruption or inaccessible files
- Authentication failures

**Recommended Actions:**
- Review transfer operation logs for specific errors
- Verify source and destination permissions
- Check storage quota and availability
- Validate file integrity and accessibility
- Retry failed transfers after resolving issues
- Implement error monitoring and alerting

### Action failed
**Alert Description:** Indicates data was not transferred as expected, representing complete transfer operation failure.

**Possible Causes:**
- Source or destination system failures
- Network interruptions
- Permission or authentication issues
- Storage space limitations
- Configuration errors

**Recommended Actions:**
- Check transfer job status and logs
- Verify source and destination system health
- Validate configuration settings
- Ensure adequate storage space
- Retry transfer operations
- Contact support if issues persist