# User Management API Documentation

## 1. Listar Usuarios (`GET /api/users/`)

Obtiene una lista paginada de todos los usuarios registrados en el sistema.

**Input (Request):**
- Headers: `Authorization: Bearer <token>`
- Query Parameters opcionales: `page` (número de página).

**Output (Response):** `200 OK`
```json
{
  "count": 2,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "username": "admin",
      "email": "admin@example.com",
      "first_name": "Admin",
      "last_name": "System"
    },
    {
      "id": 2,
      "username": "jdoe",
      "email": "jdoe@example.com",
      "first_name": "John",
      "last_name": "Doe"
    }
  ]
}
```

---

## 2. Obtener un Usuario (`GET /api/users/{id}/`)

Obtiene los detalles de un único usuario.

**Input (Request):**
- Path Parameter: `id` (entero, ID del usuario)
- Headers: `Authorization: Bearer <token>`

**Output (Response):** `200 OK`
```json
{
  "id": 2,
  "username": "jdoe",
  "email": "jdoe@example.com",
  "first_name": "John",
  "last_name": "Doe"
}
```

---

## 3. Crear un Usuario (`POST /api/users/`)

Registra un nuevo usuario en la base de datos y se encarga automáticamente de cifrar (hashear) su contraseña de forma segura.

**Input (Request JSON Body):**
- **Headers:** `Authorization: Bearer <token>`, `Content-Type: application/json`
```json
{
  "username": "new_user",
  "password": "securepassword123",
  "email": "new_user@example.com",
  "first_name": "New",
  "last_name": "User",
  "business_id": "UUID-del-negocio" // Opcional, asocia automáticamente al negocio
}
```
> **Nota:** `username` y `password` son típicamente obligatorios (según la clase interna de Django User), los otros son opcionales.

**Output (Response - Éxito):** `201 Created`
```json
{
  "id": 3,
  "username": "new_user",
  "email": "new_user@example.com",
  "first_name": "New",
  "last_name": "User"
}
```
*(Nota: El password es `write_only` y no se devuelve nunca en la respuesta por seguridad)*

---

## 4. Actualizar un Usuario (`PUT /api/users/{id}/` o `PATCH /api/users/{id}/`)

Actualiza la información de un usuario existente. Si el body incluye el campo `password`, el sistema la hasheará y reemplazará la anterior contraseña. Si incluye un nuevo `business_id`, se creará o actualizará su asociación con un negocio.

**Input para PUT (Reemplazo completo, todos los valores requeridos se esperan):**
```json
{
  "username": "updated_user",
  "password": "newpassword123",
  "email": "updated@example.com",
  "first_name": "Updated",
  "last_name": "Name",
  "business_id": "UUID-del-negocio"
}
```

**Input para PATCH (Reemplazo parcial):**
```json
{
  "email": "new_email@example.com",
  "password": "newpassword123"
}
```

**Output (Response):** `200 OK`
```json
{
  "id": 3,
  "username": "updated_user",
  "email": "new_email@example.com",
  "first_name": "New",
  "last_name": "User"
}
```

---

## 5. Eliminar un Usuario (`DELETE /api/users/{id}/`)

Elimina al usuario permanentemente de la base de datos.

**Input (Request):**
- Path Parameter: `id` (entero, ID del usuario)

**Output (Response):** `204 No Content`
*(Cuerpo vacío)*

---

## 6. Asignar un Rol (`POST /api/users/{id}/assign_role/`)

Crea la asociación entre el usuario y un rol en la tabla `UserRole`.

**Input (Request JSON Body):**
- Path Parameter: `id` (entero, ID del usuario)
- Headers: `Authorization: Bearer <token>`, `Content-Type: application/json`
```json
{
  "role_id": "b3e34ba4-2c26-4d0c-a960-918ff5e305e5"  // UUID del rol (idRole) extraído de /api/roles/
}
```

**Output en caso de Éxito, si no lo tenía asignado:** `201 Created`
```json
{
  "detail": "Role 'SuperAdmin' assigned correctly."
}
```

**Output en caso de Éxito, si el usuario YA tenía el rol:** `200 OK`
```json
{
  "detail": "User already has role 'SuperAdmin'."
}
```

**Output de Error (ej. Falta role_id):** `400 Bad Request`
```json
{
  "detail": "role_id is required."
}
```

**Output de Error (Rol no existente):** `404 Not Found`
```json
{
  "detail": "Role not found."
}
```
