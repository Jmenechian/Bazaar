# API Contracts

> [!NOTE]
> All REST endpoints return JSON (`application/json`). Dates use RFC 3339. UUIDs are used for all entity IDs.
> Authentication is via `Authorization: Bearer <JWT>` header unless noted otherwise.

---

## Gateway

Health check endpoints exposed directly by the API gateway. No authentication required.

| Method | Path       | Description                        | Auth | Request Body | Response                                  |
|--------|------------|------------------------------------|------|--------------|-------------------------------------------|
| `GET`  | `/livez`   | Liveness probe (process is alive)  | No   | —            | `200 OK` `{ "status": "alive" }`          |
| `GET`  | `/readyz`  | Readiness probe (dependencies up)  | No   | —            | `200 OK` `{ "status": "ready" }` or `503` |

---

## Users Service

**Prefix:** `/api/v1`

### Authentication

| Method | Path                    | Description                              | Auth | Request Body                                                  | Response                                                        |
|--------|-------------------------|------------------------------------------|------|---------------------------------------------------------------|-----------------------------------------------------------------|
| `POST` | `/auth/register`        | Register a new user account              | No   | `{ email, password, name, role? }`                            | `201` `{ user_id, email, name, role }`                          |
| `POST` | `/auth/login`           | Authenticate and receive tokens          | No   | `{ email, password }`                                         | `200` `{ access_token, refresh_token, expires_in }`             |
| `POST` | `/auth/refresh`         | Refresh an expired access token          | No   | `{ refresh_token }`                                           | `200` `{ access_token, refresh_token, expires_in }`             |
| `POST` | `/auth/password-reset`  | Request a password reset email           | No   | `{ email }`                                                   | `202` `{ message: "If the email exists, a reset link was sent" }` |

### User Profile

| Method | Path           | Description                      | Auth          | Request Body                     | Response                                     |
|--------|----------------|----------------------------------|---------------|----------------------------------|----------------------------------------------|
| `GET`  | `/users/me`    | Get current user's profile       | Bearer (any)  | —                                | `200` `{ id, email, name, role, created_at }` |
| `PUT`  | `/users/me`    | Update current user's profile    | Bearer (any)  | `{ name?, avatar_url? }`        | `200` `{ id, email, name, role }`             |
| `GET`  | `/users/{id}`  | Get a user's public profile      | Bearer (any)  | —                                | `200` `{ id, name, role, created_at }`        |

### Admin — User Management

| Method | Path                          | Description              | Auth           | Request Body | Response                                     |
|--------|-------------------------------|--------------------------|----------------|--------------|----------------------------------------------|
| `GET`  | `/admin/users`                | List all users (paginated) | Bearer (admin) | —            | `200` `{ users: [...], total, page, limit }` |
| `PUT`  | `/admin/users/{id}/block`     | Block a user account     | Bearer (admin) | `{ reason }` | `200` `{ id, status: "blocked" }`            |
| `PUT`  | `/admin/users/{id}/unblock`   | Unblock a user account   | Bearer (admin) | —            | `200` `{ id, status: "active" }`             |

---

## Catalog Service

**Prefix:** `/api/v1`

### Products

| Method   | Path              | Description                       | Auth            | Request Body                                                       | Response                                              |
|----------|--------------------|-----------------------------------|-----------------|--------------------------------------------------------------------|-------------------------------------------------------|
| `GET`    | `/products`        | List products (paginated)         | No              | —                                                                  | `200` `{ products: [...], total, page, limit }`       |
| `GET`    | `/products/{id}`   | Get product by ID                 | No              | —                                                                  | `200` `{ id, name, price, category, attributes, ... }`|
| `POST`   | `/products`        | Create a new product              | Bearer (seller) | `{ name, description, price, category, attributes, images[] }`    | `201` `{ id, name, price, ... }`                      |
| `PUT`    | `/products/{id}`   | Update a product                  | Bearer (seller) | `{ name?, description?, price?, category?, attributes? }`         | `200` `{ id, name, price, ... }`                      |
| `DELETE` | `/products/{id}`   | Soft-delete a product             | Bearer (seller) | —                                                                  | `204 No Content`                                      |

### Search

| Method | Path                | Description                          | Auth | Request Body | Response                                         |
|--------|---------------------|--------------------------------------|------|--------------|--------------------------------------------------|
| `GET`  | `/products/search`  | Full-text search with filters        | No   | —            | `200` `{ products: [...], total, page, limit }`  |

**Query Parameters:**

| Parameter   | Type     | Description                              | Example                 |
|-------------|----------|------------------------------------------|-------------------------|
| `q`         | `string` | Free-text search query                   | `q=wireless mouse`      |
| `category`  | `string` | Filter by category slug                  | `category=electronics`  |
| `min_price` | `number` | Minimum price filter                     | `min_price=10.00`       |
| `max_price` | `number` | Maximum price filter                     | `max_price=50.00`       |
| `sort`      | `string` | Sort order: `price_asc`, `price_desc`, `newest`, `relevance` | `sort=price_asc` |
| `page`      | `int`    | Page number (default: 1)                 | `page=2`                |
| `limit`     | `int`    | Items per page (default: 20, max: 100)   | `limit=10`              |

### Categories

| Method | Path           | Description                     | Auth | Request Body | Response                                          |
|--------|----------------|---------------------------------|------|--------------|---------------------------------------------------|
| `GET`  | `/categories`  | List all product categories     | No   | —            | `200` `{ categories: [{ id, name, slug, count }] }` |

### Reviews

| Method | Path                       | Description                      | Auth         | Request Body                       | Response                                             |
|--------|----------------------------|----------------------------------|--------------|------------------------------------|------------------------------------------------------|
| `POST` | `/products/{id}/reviews`   | Submit a review for a product    | Bearer (any) | `{ rating (1-5), comment }`       | `201` `{ id, product_id, user_id, rating, comment }` |
| `GET`  | `/products/{id}/reviews`   | List reviews for a product       | No           | —                                  | `200` `{ reviews: [...], average_rating, total }`    |

### Seller Reputation

| Method | Path                       | Description                         | Auth | Request Body | Response                                                         |
|--------|----------------------------|-------------------------------------|------|--------------|------------------------------------------------------------------|
| `GET`  | `/sellers/{id}/reputation` | Get a seller's aggregated reputation | No   | —            | `200` `{ seller_id, avg_rating, total_reviews, total_sales }`    |

### Wishlist

| Method   | Path                        | Description                        | Auth         | Request Body | Response                                          |
|----------|-----------------------------|------------------------------------|--------------|--------------|---------------------------------------------------|
| `GET`    | `/wishlist`                 | Get current user's wishlist        | Bearer (any) | —            | `200` `{ items: [{ product_id, added_at }] }`     |
| `POST`   | `/wishlist/{product_id}`    | Add a product to wishlist          | Bearer (any) | —            | `201` `{ product_id, added_at }`                  |
| `DELETE` | `/wishlist/{product_id}`    | Remove a product from wishlist     | Bearer (any) | —            | `204 No Content`                                  |

### Admin — Product Management

| Method | Path                           | Description               | Auth           | Request Body | Response                              |
|--------|--------------------------------|---------------------------|----------------|--------------|---------------------------------------|
| `GET`  | `/admin/products`              | List all products (admin) | Bearer (admin) | —            | `200` `{ products: [...], total }`    |
| `PUT`  | `/admin/products/{id}/block`   | Block/hide a product      | Bearer (admin) | `{ reason }` | `200` `{ id, status: "blocked" }`     |

---

## Commerce Service

**Prefix:** `/api/v1`

### Cart

| Method   | Path                          | Description                              | Auth         | Request Body                  | Response                                            |
|----------|-------------------------------|------------------------------------------|--------------|-------------------------------|-----------------------------------------------------|
| `GET`    | `/cart`                       | Get current user's cart                  | Bearer (any) | —                             | `200` `{ items: [{ product_id, quantity, price }], total }` |
| `POST`   | `/cart/items`                 | Add an item to the cart                  | Bearer (any) | `{ product_id, quantity }`    | `201` `{ product_id, quantity, price }`             |
| `PUT`    | `/cart/items/{product_id}`    | Update item quantity in cart             | Bearer (any) | `{ quantity }`                | `200` `{ product_id, quantity, price }`             |
| `DELETE` | `/cart/items/{product_id}`    | Remove an item from the cart             | Bearer (any) | —                             | `204 No Content`                                    |

### Checkout

| Method | Path        | Description                                  | Auth         | Request Body                                         | Response                                                   |
|--------|-------------|----------------------------------------------|--------------|------------------------------------------------------|------------------------------------------------------------|
| `POST` | `/checkout` | Initiate checkout (triggers saga orchestration) | Bearer (any) | `{ shipping_address, payment_method_id, coupon_code? }` | `202` `{ order_id, status: "processing", saga_id }`       |

> [!IMPORTANT]
> Checkout returns `202 Accepted` because the saga runs asynchronously. Poll `GET /orders/{id}` or subscribe to WebSocket notifications for order status updates.

### Orders

| Method | Path                       | Description                          | Auth            | Request Body | Response                                                       |
|--------|----------------------------|--------------------------------------|-----------------|--------------|-----------------------------------------------------------------|
| `GET`  | `/orders`                  | List current user's orders (paginated) | Bearer (any)   | —            | `200` `{ orders: [...], total, page, limit }`                  |
| `GET`  | `/orders/{id}`             | Get order details                    | Bearer (owner)  | —            | `200` `{ id, status, items, total, shipping, timeline, ... }`  |
| `PUT`  | `/orders/{id}/cancel`      | Cancel an order (if cancellable)     | Bearer (owner)  | `{ reason? }`| `200` `{ id, status: "cancelled" }`                            |
| `PUT`  | `/orders/{id}/ship`        | Mark order as shipped                | Bearer (seller) | `{ tracking_number?, carrier? }` | `200` `{ id, status: "shipped" }`                |
| `PUT`  | `/orders/{id}/deliver`     | Mark order as delivered              | Bearer (seller) | —            | `200` `{ id, status: "delivered" }`                            |

### Coupons

| Method | Path                | Description                          | Auth            | Request Body                                              | Response                                                   |
|--------|---------------------|--------------------------------------|-----------------|-----------------------------------------------------------|------------------------------------------------------------|
| `POST` | `/coupons`          | Create a new coupon                  | Bearer (seller) | `{ code, discount_type, discount_value, min_order?, expires_at? }` | `201` `{ id, code, discount_type, ... }`        |
| `GET`  | `/coupons`          | List seller's coupons                | Bearer (seller) | —                                                         | `200` `{ coupons: [...] }`                                 |
| `POST` | `/coupons/validate` | Validate a coupon code against a cart | Bearer (any)    | `{ code, cart_total }`                                    | `200` `{ valid, discount_amount, message }`                |

### Metrics & Analytics

| Method | Path                      | Description                              | Auth           | Request Body | Response                                                     |
|--------|---------------------------|------------------------------------------|----------------|--------------|--------------------------------------------------------------|
| `GET`  | `/metrics/orders`         | Order volume metrics (by period)         | Bearer (admin) | —            | `200` `{ total_orders, by_status: {...}, by_period: [...] }` |
| `GET`  | `/metrics/gmv`            | Gross Merchandise Value metrics          | Bearer (admin) | —            | `200` `{ total_gmv, by_period: [...], currency }`            |
| `GET`  | `/metrics/top-products`   | Top-selling products                     | Bearer (admin) | —            | `200` `{ products: [{ id, name, units_sold, revenue }] }`   |
| `GET`  | `/metrics/export/csv`     | Export order data as CSV                 | Bearer (admin) | —            | `200` CSV file (`Content-Type: text/csv`)                    |

**Common query parameters for metrics endpoints:**

| Parameter    | Type     | Description                                      | Example               |
|--------------|----------|--------------------------------------------------|-----------------------|
| `period`     | `string` | Aggregation period: `day`, `week`, `month`       | `period=week`         |
| `start_date` | `string` | Start date (RFC 3339)                            | `start_date=2026-09-01` |
| `end_date`   | `string` | End date (RFC 3339)                              | `end_date=2026-09-30` |
| `limit`      | `int`    | Number of results (for top-products, default: 10)| `limit=20`            |

### Admin — Order Management

| Method | Path            | Description                        | Auth           | Request Body | Response                                       |
|--------|-----------------|------------------------------------|----------------|--------------|------------------------------------------------|
| `GET`  | `/admin/orders` | List all orders (admin, paginated) | Bearer (admin) | —            | `200` `{ orders: [...], total, page, limit }`  |

---

## Notifications Service

**Prefix:** `/api/v1`

| Method | Path                      | Description                              | Auth         | Request Body | Response                                                  |
|--------|---------------------------|------------------------------------------|--------------|--------------|-----------------------------------------------------------|
| `GET`  | `/notifications`          | Get user's notification history (paginated) | Bearer (any) | —            | `200` `{ notifications: [{ id, type, message, read, created_at }], total, unread_count }` |
| `PUT`  | `/notifications/{id}/read`| Mark a notification as read              | Bearer (any) | —            | `200` `{ id, read: true }`                               |

---

## gRPC — Warehouse Edge Service

Communication between the cloud Commerce service and the Raspberry Pi edge node uses **gRPC** with Protocol Buffers.

**Proto package:** `bazaar.warehouse.v1`

### Service Definition

```protobuf
syntax = "proto3";

package bazaar.warehouse.v1;

service WarehouseSync {
  // Bidirectional stream for real-time stock synchronization.
  // Edge pushes local stock changes; cloud pushes authoritative updates.
  rpc SyncStock(stream StockUpdate) returns (stream SyncResponse);

  // Pull orders pending fulfillment at this warehouse.
  rpc GetPendingOrders(WarehouseRequest) returns (PendingOrdersList);

  // Mark an order as physically fulfilled (picked, packed, ready to ship).
  rpc FulfillOrder(FulfillRequest) returns (FulfillResponse);

  // Periodic heartbeat from edge → cloud for connectivity & health monitoring.
  rpc Heartbeat(HealthStatus) returns (Ack);
}
```

### RPC Details

| RPC                | Type                     | Description                                                                 |
|--------------------|--------------------------|-----------------------------------------------------------------------------|
| `SyncStock`        | Bidirectional streaming  | Edge streams `StockUpdate` messages (product_id, delta, timestamp). Cloud responds with `SyncResponse` (ack/reject per update). |
| `GetPendingOrders` | Unary                   | Edge requests orders assigned to its warehouse that are pending fulfillment. Returns a list of orders with items to pick. |
| `FulfillOrder`     | Unary                   | Edge reports that a specific order has been physically fulfilled. Triggers order status transition to `shipped`. |
| `Heartbeat`        | Unary                   | Edge sends device health (uptime, disk usage, sync queue depth). Cloud responds with `Ack` and optional commands. |

### Message Types

```protobuf
message StockUpdate {
  string product_id = 1;
  int32  delta      = 2;  // positive = restock, negative = consumed
  string timestamp  = 3;  // RFC 3339
  string idempotency_key = 4;
}

message SyncResponse {
  string idempotency_key = 1;
  bool   accepted        = 2;
  string reason          = 3;  // populated if rejected
}

message WarehouseRequest {
  string warehouse_id = 1;
  int32  limit        = 2;
}

message PendingOrdersList {
  repeated PendingOrder orders = 1;
}

message PendingOrder {
  string order_id = 1;
  repeated OrderItem items = 2;
  string priority  = 3;  // "normal", "express"
}

message OrderItem {
  string product_id   = 1;
  string product_name = 2;
  int32  quantity      = 3;
  string location_hint = 4;  // warehouse shelf/bin location
}

message FulfillRequest {
  string order_id     = 1;
  string warehouse_id = 2;
  string fulfilled_by = 3;  // operator ID
  string timestamp    = 4;
}

message FulfillResponse {
  bool   success = 1;
  string message = 2;
}

message HealthStatus {
  string warehouse_id    = 1;
  int64  uptime_seconds  = 2;
  float  disk_usage_pct  = 3;
  int32  pending_sync    = 4;  // number of unsynced operations
  string version         = 5;  // edge software version
}

message Ack {
  bool   ok      = 1;
  string command = 2;  // optional: "update", "restart", "noop"
}
```

---

## Common Response Patterns

### Error Response

All endpoints return errors in a consistent format:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Price must be greater than 0",
    "details": [
      { "field": "price", "message": "must be > 0" }
    ]
  }
}
```

### Pagination

Paginated endpoints accept `page` (default: 1) and `limit` (default: 20, max: 100) query parameters and return:

```json
{
  "data": [...],
  "total": 150,
  "page": 2,
  "limit": 20
}
```

### HTTP Status Codes

| Code  | Usage                                                           |
|-------|-----------------------------------------------------------------|
| `200` | Successful read or update                                       |
| `201` | Resource created                                                |
| `202` | Accepted (async processing — e.g., checkout)                    |
| `204` | Successful delete (no body)                                     |
| `400` | Validation error / bad request                                  |
| `401` | Missing or invalid authentication token                         |
| `403` | Insufficient permissions (wrong role)                           |
| `404` | Resource not found                                              |
| `409` | Conflict (e.g., duplicate email, already reviewed)              |
| `422` | Business logic error (e.g., insufficient stock, invalid coupon) |
| `429` | Rate limit exceeded                                             |
| `500` | Internal server error                                           |
| `503` | Service unavailable (dependency down)                           |
