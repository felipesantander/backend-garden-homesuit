# API Documentation - Garden HomeSuit

This document provides a comprehensive guide to the API endpoints defined in the `core` application, designed for use by the frontend development team.

## Authentication

The API uses JWT (JSON Web Token) for authentication. All protected endpoints require a `Bearer` token in the `Authorization` header.

### Endpoints (Unprotected)
- **POST `/api/token/`**: Obtain access and refresh tokens.
  - Body: `{"username": "...", "password": "..."}`
  - Response: `{"access": "...", "refresh": "..."}`
- **POST `/api/token/refresh/`**: Refresh the access token.
  - Body: `{"refresh": "..."}`
- **POST `/api/token/verify/`**: Verify if a token is valid.
  - Body: `{"token": "..."}`
- **POST `/api/ingest/`**: Ingest sensor data (Unprotected by design for machine connectivity).
  - Body: See [Data Ingestion](#data-ingestion) below.

## RBAC (Role-Based Access Control)

Access to protected endpoints (`/api/*` except `token` and `ingest`) is managed by a middleware that checks the `role` claim in your JWT.

- **SuperAdmin**: Has full access to all endpoints.
- **Other Roles**: Permissions are defined per-role in the `Permission` and `Role` models.

---

## Core Endpoints (Protected)

Base path: `/api/`

### 1. Businesses
- **GET `/api/businesses/`**: List all businesses.
- **POST `/api/businesses/`**: Create a new business.
  - Body: `{"name": "...", "user": <user_id>}`
- **GET/PATCH/DELETE `/api/businesses/<idBusiness>/`**

### 2. Gardens
- **GET `/api/gardens/`**: List all gardens.
- **POST `/api/gardens/`**: Create a new garden for a business.
  - Body: `{"name": "...", "business": "<idBusiness>"}`
- **GET/PATCH/DELETE `/api/gardens/<idGarden>/`**

### 3. Machines
- **GET `/api/machines/`**: List all registered machines.
- **POST `/api/machines/`**: Register a new machine in a garden.
  - Body: `{"serial": "SER_...", "Name": "...", "garden": "<idGarden>"}`
- **GET/PATCH/DELETE `/api/machines/<machineId>/`**

### 4. Channels
- **GET `/api/channels/`**: List all data channels.
- **POST `/api/channels/`**: Create a new channel.
  - Body: `{"name": "...", "unit": "...", "business": "<idBusiness>"}`
- **GET/PATCH/DELETE `/api/channels/<idChannel>/`**

### 5. Data (Bucketed)
Sensors data is stored in hourly buckets.
- **GET `/api/data/`**: List all data buckets.
- **GET `/api/data/latest/?serial=<SN>`**: Get the last reading for each data type for a specific machine serial.
- **GET/DELETE `/api/data/<idData>/`**: Retrieve or delete a specific hour's bucket for a machine/type.
- **Structure**:
  - `base_date`: Start of the hour (ISO).
  - `count`: Number of readings in the bucket.
  - `readings`: Array of `{"v": value, "t": timestamp, "f": frequency}`.

### 6. Notifications
- **GET `/api/notifications/`**: List user notifications.
- **PATCH `/api/notifications/<idNotification>/`**: e.g., Mark as seen `{"seen": true}`.

### 7. Configuration Channels
Map data types to specific channels for a machine.
- **GET `/api/configuration-channels/`**: List all mappings.
- **POST `/api/configuration-channels/`**: Create a new mapping between a machine, data type, and channel.
  - Body: `{"machine": "<machine_id>", "channel": "<idChannel>", "type": "voltage/current/...", "serial": "..."}`
- **GET/PATCH/DELETE `/api/configuration-channels/<id>/`**: Retrieve, update or delete a mapping.

### 8. Machine Candidates
Auto-discovered machines via MQTT that are not yet registered.
- **GET `/api/machine-candidates/`**: List all machine candidates.
- **POST `/api/machine-candidates/`**: Create a new machine candidate manually.
  - Body: `{"serial": "...", "types": ["...", ...]}`
- **GET `/api/machine-candidates/<id>/`**: Retrieve a specific candidate.
- **PATCH `/api/machine-candidates/<id>/`**: Update candidate fields.
- **DELETE `/api/machine-candidates/<id>/`**: Remove a candidate.

---

## RBAC Management

### 9. Permissions
Define endpoint-level access patterns and resource-level scoping.
- **GET/POST `/api/permissions/`**
  - Body:
    ```json
    {
        "name": "...",
        "endpoints": [{"path": "/api/...", "host": "*", "method": "GET/*"}],
        "gardens": ["<idGarden1>", "<idGarden2>"],
        "businesses": ["<idBusiness1>"],
        "machines": ["<idMachine1>"],
        "components": ["admin_panel"]
    }
    ```

### 10. Roles
Group permissions.
- **GET/POST `/api/roles/`**
  - Body: `{"name": "Developer", "permissions": [<idPermission>, ...]}`

### 11. User Roles
Assign roles to users.
- **GET/POST `/api/user-roles/`**
  - Body: `{"user": <user_id>, "role": <idRole>}`

---

## Data Ingestion

Designed for high-frequency intake. Does not require JWT but performs validation.

- **POST `/api/ingest/`**
- **Payload Schema**:
```json
{
    "frequency": "5_seconds",
    "value": 220.5,
    "type": "voltage",
    "serial_machine": "SER_001",
    "machineId": "uuid...",
    "channelId": "uuid...",
    "date_of_capture": "2026-02-18T10:00:00Z" (optional)
}
```
