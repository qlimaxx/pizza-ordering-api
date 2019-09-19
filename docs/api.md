# API Endpoint URL

`http://localhost:8000/api`

# List pizzas

While creating or updating an order, you will need some pizzas IDs. You can use this endpoint to get some IDs.

- **GET** `/pizzas/`

# Create an order

 Creating a new order will create a new customer if the name of customer doesn't exist in the database otherwise it will use the existing customer.

- **POST** `/orders/`

-   #### Request body

    | Field | Type | Required |
    |--------|:----:|------------:|
    | customer | Dict | Yes |
    | customer > name | String | Yes |
    | customer > address | String | Yes |
    | customer > phone | String | No |
    | pizzas | List | Yes |
    | pizzas > id | UUID | Yes |
    | pizzas > details | List | Yes |
    | pizzas > details >  size | Enum(Small, Medium, Large) | Yes |
    | pizzas > details >  count | Number | Yes |

- #### Example

    ```json
    {
      "customer": {
        "name": "Melissa Mintrim",
        "address": "39 Armistice Lane",
        "phone": "926-643-6238"
      },
      "pizzas": [{
        "id": "6cf64e9a-9871-412a-ab4d-173a92af270f",
        "details": [{
          "size": "Small",
          "count": 3
        }, {
          "size": "Medium",
          "count": 2
        }]
      }]
    }
    ```

# Update an order

- **PUT** `/orders/<order_id>/`

- #### Request body

    | Field | Type | Required |
    |--------|:----:|:--------|
    | customer | Dict | Yes |
    | customer > name | String | Yes |
    | customer > address | String | Yes |
    | customer > phone | String | No |
    | pizzas | List | Yes |
    | pizzas > id | UUID | Yes |
    | pizzas > details | List | Yes |
    | pizzas > details >  size | Enum(Small, Medium, Large) | Yes |
    | pizzas > details >  count | Number | Yes |

-   #### Example

    ```json
    {
      "customer": {
        "name": "Melissa Mintrim",
        "address": "39 Armistice Lane",
        "phone": "926-643-6238"
      },
      "pizzas": [{
        "id": "6cf64e9a-9871-412a-ab4d-173a92af270f",
        "details": [{
          "size": "Small",
          "count": 3
        }, {
          "size": "Medium",
          "count": 2
        }]
      }]
    }
    ```

# Update an order status

- **PUT** `/orders/<order_id>/status/`

- #### Request body

    | Field | Type | Required |
    |--------|:----:|------------:|
    | status | Enum(Processing, Delivering, Delivered) | Yes |

- #### Example

    ```json
    {"status": "Delivered"}
    ```

# Retrieve an order

- **GET** `/orders/<order_id>/`

# Remove an order

- **DELETE** `/orders/<order_id>/`

# List orders

- **GET** `/orders/`

# Filter orders

- **GET** `/orders/<order_id>/status/?status=<status>&customer=<customer>`

- #### Parameters

    | Field | Type | Required |
    |--------|:----:|--------:|
    | status | Enum(Processing, Delivering, Delivered) | No |
    | customer | UUID | No |
