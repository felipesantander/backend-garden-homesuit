# Documentación API de Alertas (Alerts)

Esta documentación describe el endpoint para gestionar Alertas y el nuevo sistema de evaluación lógica con operadores AND/OR.

## Gestión de Alertas

### **POST `/api/alerts/`**
Crea una nueva alerta con uno o más criterios de evaluación.

#### **Cuerpo de la Petición (Request Body)**
```json
{
  "name": "Nombre de la alerta (String)",
  "duration": "Segundos (Integer) - Ventana de tiempo hacia atrás para analizar datos",
  "data_frequency": "Frecuencia de datos (e.g., '1_minutes', '5_seconds')",
  "machines": ["Lista de UUIDs de Máquinas"],
  "contacts": [
    {
      "name": "Nombre del contacto",
      "phone": "Teléfono (Formato 569...)"
    }
  ],
  "is_active": "Boolean (Por defecto true)",
  "criteria": [
    {
      "channel": "UUID del Canal (Channel ID)",
      "condition": "Operador ('>', '<', '=')",
      "threshold": "Valor umbral (Float)",
      "logical_operator": "Operador Lógico ('AND' o 'OR')",
      "order": "Orden de evaluación (Optional, se auto-asigna por índice)"
    }
  ]
}
```

### **Lógica de Evaluación (AND/OR)**

El motor de alertas evalúa los criterios basándose en su `order` y el `logical_operator`. 

#### **Reglas de funcionamiento:**
1. **Primer Criterio**: El `logical_operator` del primer criterio (índice 0 o menor `order`) se ignora, ya que no tiene un resultado previo con el cual vincularse.
2. **Criterios Sucesivos**: El operador definido en el criterio `N` determina cómo se une su resultado con el resultado acumulado de `1 a N-1`.
3. **Precedencia**: Se sigue la precedencia estándar de Python (`AND` se evalúa antes que `OR`).

#### **Ejemplo de Payload Lógico:**
Para implementar la lógica: `Voltaje > 240` **O** (`Corriente < 1.0` **Y** `Potencia > 500`):

```json
{
  "name": "Alerta Compleja de Energía",
  "criteria": [
    { 
      "channel": "UUID_VOLTAJE", 
      "condition": ">", 
      "threshold": 240 
    },
    { 
      "channel": "UUID_CORRIENTE", 
      "condition": "<", 
      "threshold": 1.0, 
      "logical_operator": "OR" 
    },
    { 
      "channel": "UUID_POTENCIA", 
      "condition": ">", 
      "threshold": 500.0, 
      "logical_operator": "AND" 
    }
  ]
}
```
**Resultado evaluado:**
`Resultado1 OR (Resultado2 AND Resultado3)`

---

### **GET `/api/alerts/`**
Lista todas las alertas definidas.

### **GET/PATCH/DELETE `/api/alerts/<idAlert>/`**
Gestiona una alerta específica. Al hacer `PATCH` de `criteria`, se reemplazan los criterios existentes por los nuevos enviados.

## Historial de Alertas

### **GET `/api/alert-history/`**
Lista los registros de alertas que han sido disparadas.
- Incluye `machine`, `alert` y `details` (con los valores exactos y criterios que cumplieron el disparo).
