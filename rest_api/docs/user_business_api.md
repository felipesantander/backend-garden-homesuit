# Documentación API - UserBusiness

Los endpoints de `UserBusiness` sirven para administrar de forma directa la relación "uno a uno" entre usuarios de la plataforma y el `Business` u organización a la cual le pertenecen.

## 1. Listar Relaciones Usuario-Negocio (`GET /api/user-businesses/`)

Obtiene una lista paginada de todas las relaciones creadas entre un usuario y un negocio (`Business`).

**Input (Request):**
- **Headers:** `Authorization: Bearer <token>`
- **Query Parameters (opcional):** `page` (número de página).

**Output (Response):** `200 OK`
```json
{
  "count": 1,
  "next": null,
  "previous": null,
  "results": [
    {
      "idUserBusiness": "fc0bfea4-e8ba-44f3-80f0-323a2d2105eb",
      "user": 3,
      "business": "b8a82d0d-cdb8-4c9f-8de4-f0afae616f73"
    }
  ]
}
```
*(Nota: `user` es el ID entero del usuario y `business` es el UUID del negocio)*

---

## 2. Obtener Detalles de una Relación Específica (`GET /api/user-businesses/{id}/`)

Permite obtener los detalles de una relación específica basada en su Identificador (UUID de la relación `UserBusiness`).

**Input (Request):**
- **Path Parameter:** `id` (UUID, de tipo `idUserBusiness`)
- **Headers:** `Authorization: Bearer <token>`

**Output (Response):** `200 OK`
```json
{
  "idUserBusiness": "fc0bfea4-e8ba-44f3-80f0-323a2d2105eb",
  "user": 3,
  "business": "b8a82d0d-cdb8-4c9f-8de4-f0afae616f73"
}
```

---

## 3. Crear Directamente una Relación (`POST /api/user-businesses/`)

Asigna un usuario a un `Business`. Es importante recordar que el modelo fue diseñado con un constraint de **uno-a-uno (OneToOneField)** hacia el usuario, lo que quiere decir que si intentas crear una relación para un usuario que YA pertenece a un negocio, arrojará un error 400 avisándote que este registro único ya existe.

**Input (Request JSON Body):**
- **Headers:** `Authorization: Bearer <token>`, `Content-Type: application/json`
```json
{
  "user": 3,
  "business": "b8a82d0d-cdb8-4c9f-8de4-f0afae616f73"
}
```

**Output (Response - Éxito):** `201 Created`
```json
{
  "idUserBusiness": "d04a43b2-658f-4cf2-83e9-a0ff2c448bbd",
  "user": 3,
  "business": "b8a82d0d-cdb8-4c9f-8de4-f0afae616f73"
}
```

---

## 4. Reasignar el Negocio a un Usuario (`PUT /api/user-businesses/{id}/` o `PATCH /api/user-businesses/{id}/`)

Edita el registro intermedio de relación. Generalmente se usa si deseas cambiar al usuario de un `Business` hacia otro diferente. Para hacer esto se referencia la ID de la relación `idUserBusiness`.

**Input para PUT o PATCH:**
```json
{
  "business": "NUEVO-UUID-DEL-NEGOCIO"
}
```

**Output (Response):** `200 OK`
```json
{
  "idUserBusiness": "fc0bfea4-e8ba-44f3-80f0-323a2d2105eb",
  "user": 3,
  "business": "NUEVO-UUID-DEL-NEGOCIO"
}
```

---

## 5. Eliminar la Relación (`DELETE /api/user-businesses/{id}/`)

Borra la relación entre un usuario y un `Business`. Esto provocará que el usuario quede en un estado de "huérfano" por parte de la jerarquía de negocios. (El usuario NO es eliminado; sólo la relación).

**Input (Request):**
- **Path Parameter:** `id` (UUID de la relación)
- **Headers:** `Authorization: Bearer <token>`

**Output (Response):** `204 No Content`
*(Cuerpo de respuesta vacío, la relación fue eliminada exitosamente)*
