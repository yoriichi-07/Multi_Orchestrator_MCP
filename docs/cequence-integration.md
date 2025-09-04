# Cequence AI Gateway Integration Guide

## Overview

The Autonomous Software Foundry includes comprehensive integration with Cequence AI Gateway for advanced analytics, security monitoring, and operational intelligence. This integration provides real-time insights into application usage, security events, and performance metrics.

## Configuration

### Environment Variables

Add the following environment variables to your `.env` file:

```bash
# Cequence AI Gateway Configuration
CEQUENCE_GATEWAY_URL=https://your-cequence-gateway.com
CEQUENCE_GATEWAY_ID=your_gateway_id_here
CEQUENCE_API_KEY=your_cequence_api_key_here
CEQUENCE_ANALYTICS_BUFFER_SIZE=100
CEQUENCE_ENABLE_SECURITY_MONITORING=true
CEQUENCE_ENABLE_PERFORMANCE_MONITORING=true
```

### Configuration Options

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `CEQUENCE_GATEWAY_URL` | Base URL for Cequence AI Gateway API | None | No |
| `CEQUENCE_GATEWAY_ID` | Unique identifier for your gateway | None | No |
| `CEQUENCE_API_KEY` | Authentication key for Cequence API | None | No |
| `CEQUENCE_ANALYTICS_BUFFER_SIZE` | Number of metrics to buffer before sending | 100 | No |
| `CEQUENCE_ENABLE_SECURITY_MONITORING` | Enable security event tracking | true | No |
| `CEQUENCE_ENABLE_PERFORMANCE_MONITORING` | Enable performance analytics | true | No |

## Features

### 1. Request Analytics

Every HTTP request is automatically tracked with:
- Request method, path, and parameters
- Response status codes and processing time
- Authentication context (user ID, client ID, scopes)
- Risk score calculation based on request patterns
- Client IP and user agent information

### 2. Agent Operation Tracking

All MCP tool executions are monitored:
- Operation type (generation, testing, deployment, etc.)
- Agent type (orchestrator, specialist agents)
- Success/failure status and error details
- Performance metrics (duration, resource usage)
- Custom metadata for business intelligence

### 3. Security Event Monitoring

Security-related events are automatically detected and logged:
- Authentication failures and token issues
- Rate limiting violations
- Suspicious request patterns
- Access control violations
- Security risk scoring

### 4. Real-time Dashboard

Access the integrated dashboard at `/static/demo_dashboard.html`:
- Live metrics visualization with Chart.js
- Connection status monitoring
- Request volume and performance trends
- Security event alerts

## API Integration

### Tracked Metrics Structure

```json
{
  "timestamp": "2024-01-15T10:30:00Z",
  "correlation_id": "uuid-correlation-id",
  "request": {
    "method": "POST",
    "path": "/mcp/v1/tools/generate_application",
    "query_params": {},
    "headers": {"user-agent": "client-name"},
    "client_ip": "192.168.1.100"
  },
  "response": {
    "status_code": 200,
    "headers": {"content-type": "application/json"},
    "processing_time_ms": 1500.5
  },
  "auth_context": {
    "user_id": "user123",
    "client_id": "client456",
    "is_machine": false,
    "scopes": ["tools:generate"]
  },
  "risk_score": 0.3
}
```

### Agent Operations

```json
{
  "timestamp": "2024-01-15T10:30:00Z",
  "correlation_id": "uuid-correlation-id",
  "operation": {
    "type": "application_generation",
    "agent_type": "orchestrator",
    "duration_ms": 2500.0,
    "success": true,
    "metadata": {
      "project_type": "fullstack",
      "user_id": "user123"
    }
  }
}
```

### Security Events

```json
{
  "timestamp": "2024-01-15T10:30:00Z",
  "correlation_id": "uuid-correlation-id",
  "security_event": {
    "type": "authentication_failure",
    "severity": "warning",
    "description": "Invalid JWT token provided",
    "client_ip": "192.168.1.100",
    "user_id": "suspicious_user",
    "risk_indicators": ["auth_failure", "repeated_attempts"]
  }
}
```

## Risk Scoring

The system automatically calculates risk scores (0.0 to 1.0) based on:

- **Request patterns**: Admin endpoints, generation requests
- **Authentication**: Missing auth, machine vs. human access
- **Request size**: Large payloads or suspicious content
- **Client behavior**: Request frequency, error patterns

### Risk Levels

- **0.0 - 0.3**: Low risk (routine operations)
- **0.3 - 0.6**: Medium risk (generation requests, elevated access)
- **0.6 - 0.8**: High risk (admin operations, unusual patterns)
- **0.8 - 1.0**: Critical risk (security violations, attack patterns)

## Graceful Degradation

The Cequence integration is designed to fail gracefully:

- If configuration is missing, analytics are disabled silently
- Network errors to Cequence don't affect application functionality
- Metrics are buffered locally and sent asynchronously
- Performance impact is minimal through efficient batching

## Testing

Run the comprehensive test suite:

```bash
# Test Cequence integration
pytest tests/test_cequence_integration.py -v

# Test with coverage
pytest tests/test_cequence_integration.py --cov=src.core.cequence_integration
```

## Development Mode

For local development, you can:

1. Set `CEQUENCE_GATEWAY_ID=None` to disable analytics
2. Use mock endpoints for testing
3. Enable demo mode for offline development

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure `starlette` is installed for middleware support
2. **Connection Timeouts**: Verify `CEQUENCE_GATEWAY_URL` is accessible
3. **Authentication Failures**: Check `CEQUENCE_API_KEY` validity
4. **High Memory Usage**: Reduce `CEQUENCE_ANALYTICS_BUFFER_SIZE`

### Debug Mode

Enable debug logging:

```bash
LOG_LEVEL=DEBUG
```

This will show detailed Cequence integration activity in the logs.

## Security Considerations

- API keys are automatically redacted from logs and analytics
- Authorization headers are sanitized before transmission
- Client IP addresses are analyzed for security patterns
- All metrics include correlation IDs for audit trails

## Performance Impact

- Async operation: No blocking of request processing
- Buffered metrics: Efficient batch transmission
- Lightweight middleware: <1ms overhead per request
- Graceful degradation: Zero impact when Cequence unavailable

## Support

For Cequence AI Gateway support:
- Contact your Cequence representative
- Check the Cequence documentation portal
- Review network connectivity and API access

For integration issues:
- Check application logs for Cequence-related errors
- Verify environment variable configuration
- Run the test suite to validate functionality