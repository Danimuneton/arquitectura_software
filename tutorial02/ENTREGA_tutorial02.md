
## Reflexión: ¿Por qué el `OrdenBuilder` reduce el riesgo de errores?

El patrón **Builder** reduce el riesgo de errores porque **centraliza y
encapsula** en un solo lugar toda la lógica de construcción y validación de la
orden (el cálculo del subtotal, la aplicación del IVA y la verificación de que
existan usuario y productos). Si en cambio creáramos la Orden directamente en
la vista, esa lógica quedaría dispersa y habría que repetirla y recordarla
en cada punto del código que necesite crear una orden (la vista web, la API, un
comando de administración, un test), con el riesgo constante de olvidar un paso
por ejemplo, aplicar el IVA o validar el stock o de calcular el total de forma
inconsistente entre un lugar y otro. El Builder garantiza que **toda orden nace
válida y completa**, sin importar quién la pida: su método build() es la única
puerta de entrada y rechaza con un error claro cualquier construcción con datos
insuficientes. Además, su *fluent interface* (`.con_usuario(...).con_productos(...).build()`)
hace el código legible y autoexplicativo, y mantiene la vista delgada y enfocada
únicamente en recibir la petición y delegar, respetando el principio de
responsabilidad única (SRP).

---
