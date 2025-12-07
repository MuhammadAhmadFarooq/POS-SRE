# Architecture Comparison Document

## 1. Legacy System Architecture

### 1.1 Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            LEGACY POS SYSTEM                                 │
│                        (Monolithic Desktop Application)                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                        JAVA SWING GUI LAYER                          │   │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐  │   │
│  │  │  Login   │ │ Cashier  │ │  Admin   │ │Transaction│ │ Payment  │  │   │
│  │  │Interface │ │Interface │ │Interface │ │ Interface │ │Interface │  │   │
│  │  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘  │   │
│  │       │            │            │            │            │         │   │
│  │  ┌────┴────────────┴────────────┴────────────┴────────────┴─────┐  │   │
│  │  │              BUSINESS LOGIC (Mixed with GUI)                  │  │   │
│  │  └──────────────────────────────┬───────────────────────────────┘  │   │
│  └─────────────────────────────────┼───────────────────────────────────┘   │
│                                    │                                        │
│  ┌─────────────────────────────────┼───────────────────────────────────┐   │
│  │                   TIGHTLY COUPLED COMPONENTS                         │   │
│  │                                 │                                    │   │
│  │  ┌─────────────┐  ┌─────────────┴─────────────┐  ┌─────────────┐    │   │
│  │  │  POSSystem  │  │      PointOfSale          │  │  Management │    │   │
│  │  │(Auth+System)│  │  (Abstract Transaction)   │  │ (User Mgmt) │    │   │
│  │  └──────┬──────┘  └────────────┬──────────────┘  └──────┬──────┘    │   │
│  │         │                      │                        │           │   │
│  │         │         ┌────────────┼────────────┐           │           │   │
│  │         │         │            │            │           │           │   │
│  │         │      ┌──┴──┐     ┌───┴───┐    ┌───┴───┐       │           │   │
│  │         │      │ POS │     │  POR  │    │  POH  │       │           │   │
│  │         │      │Sale │     │Rental │    │Return │       │           │   │
│  │         │      └──┬──┘     └───┬───┘    └───┬───┘       │           │   │
│  │         │         │            │            │           │           │   │
│  │         │         └────────────┼────────────┘           │           │   │
│  │         │                      │                        │           │   │
│  │  ┌──────┴──────────────────────┴────────────────────────┴──────┐    │   │
│  │  │                    Inventory (Singleton)                     │    │   │
│  │  └──────────────────────────────┬──────────────────────────────┘    │   │
│  └─────────────────────────────────┼───────────────────────────────────┘   │
│                                    │                                        │
│  ┌─────────────────────────────────┼───────────────────────────────────┐   │
│  │                         FILE-BASED DATA LAYER                        │   │
│  │                                 │                                    │   │
│  │  ┌──────────────────────────────┴──────────────────────────────┐    │   │
│  │  │                    PLAIN TEXT FILES                          │    │   │
│  │  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐            │    │   │
│  │  │  │ employee    │ │ item        │ │ user        │            │    │   │
│  │  │  │ Database.txt│ │ Database.txt│ │ Database.txt│            │    │   │
│  │  │  └─────────────┘ └─────────────┘ └─────────────┘            │    │   │
│  │  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐            │    │   │
│  │  │  │ rental      │ │ coupon      │ │ saleInvoice │            │    │   │
│  │  │  │ Database.txt│ │ Number.txt  │ │ Record.txt  │            │    │   │
│  │  │  └─────────────┘ └─────────────┘ └─────────────┘            │    │   │
│  │  └─────────────────────────────────────────────────────────────┘    │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 1.2 Problems with Legacy Architecture

1. **Monolithic Design**: All components tightly coupled
2. **No Layered Structure**: GUI mixed with business logic
3. **File-Based Storage**: No data integrity, no transactions
4. **Single User**: No concurrent access support
5. **Platform Dependent**: Desktop-only, requires installation
6. **No API**: Cannot integrate with other systems
7. **Security Issues**: Plain text passwords

---

## 2. Reengineered System Architecture

### 2.1 Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         REENGINEERED POS SYSTEM                              │
│                    (Modern Web-Based MVC Application)                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                     CLIENT LAYER (Browser)                           │   │
│  │  ┌─────────────────────────────────────────────────────────────┐    │   │
│  │  │                    HTML5 + Bootstrap 5 + JS                  │    │   │
│  │  │                                                              │    │   │
│  │  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐       │    │   │
│  │  │  │  Login   │ │  Cashier │ │   Admin  │ │ Reports  │       │    │   │
│  │  │  │   View   │ │   View   │ │   View   │ │   View   │       │    │   │
│  │  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘       │    │   │
│  │  └─────────────────────────────────────────────────────────────┘    │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │ HTTP/REST                              │
│                                    ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    PRESENTATION LAYER (Flask)                        │   │
│  │  ┌─────────────────────────────────────────────────────────────┐    │   │
│  │  │                       CONTROLLERS                            │    │   │
│  │  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐       │    │   │
│  │  │  │  Auth    │ │ Cashier  │ │  Admin   │ │   API    │       │    │   │
│  │  │  │Controller│ │Controller│ │Controller│ │Controller│       │    │   │
│  │  │  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘       │    │   │
│  │  │       │            │            │            │              │    │   │
│  │  │       └────────────┴────────────┴────────────┘              │    │   │
│  │  │                         │                                    │    │   │
│  │  │                Jinja2 Templates                              │    │   │
│  │  └─────────────────────────┼───────────────────────────────────┘    │   │
│  └────────────────────────────┼────────────────────────────────────────┘   │
│                               │                                             │
│                               ▼                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    BUSINESS LOGIC LAYER                              │   │
│  │  ┌─────────────────────────────────────────────────────────────┐    │   │
│  │  │                        SERVICES                              │    │   │
│  │  │  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐         │    │   │
│  │  │  │    Auth      │ │  Transaction │ │  Inventory   │         │    │   │
│  │  │  │   Service    │ │   Service    │ │   Service    │         │    │   │
│  │  │  └──────────────┘ └──────────────┘ └──────────────┘         │    │   │
│  │  │  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐         │    │   │
│  │  │  │   Rental     │ │   Employee   │ │   Coupon     │         │    │   │
│  │  │  │   Service    │ │   Service    │ │   Service    │         │    │   │
│  │  │  └──────────────┘ └──────────────┘ └──────────────┘         │    │   │
│  │  └─────────────────────────────────────────────────────────────┘    │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                               │                                             │
│                               ▼                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    DATA ACCESS LAYER                                 │   │
│  │  ┌─────────────────────────────────────────────────────────────┐    │   │
│  │  │                     REPOSITORIES                             │    │   │
│  │  │  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐         │    │   │
│  │  │  │   Employee   │ │     Item     │ │  Customer    │         │    │   │
│  │  │  │  Repository  │ │  Repository  │ │  Repository  │         │    │   │
│  │  │  └──────────────┘ └──────────────┘ └──────────────┘         │    │   │
│  │  │  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐         │    │   │
│  │  │  │ Transaction  │ │    Rental    │ │    Coupon    │         │    │   │
│  │  │  │  Repository  │ │  Repository  │ │  Repository  │         │    │   │
│  │  │  └──────────────┘ └──────────────┘ └──────────────┘         │    │   │
│  │  └─────────────────────────────────────────────────────────────┘    │   │
│  │                               │                                      │   │
│  │  ┌─────────────────────────────────────────────────────────────┐    │   │
│  │  │                 SQLAlchemy ORM MODELS                        │    │   │
│  │  │  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐     │    │   │
│  │  │  │Employee│ │  Item  │ │Customer│ │  Trans │ │ Rental │     │    │   │
│  │  │  └────────┘ └────────┘ └────────┘ └────────┘ └────────┘     │    │   │
│  │  └─────────────────────────────────────────────────────────────┘    │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                               │                                             │
│                               ▼                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    DATABASE LAYER                                    │   │
│  │  ┌─────────────────────────────────────────────────────────────┐    │   │
│  │  │              SQLite / PostgreSQL                             │    │   │
│  │  │  ┌────────────────────────────────────────────────────┐     │    │   │
│  │  │  │                RELATIONAL TABLES                    │     │    │   │
│  │  │  │  ┌──────────┐ ┌──────────┐ ┌──────────┐            │     │    │   │
│  │  │  │  │employees │ │  items   │ │customers │            │     │    │   │
│  │  │  │  └──────────┘ └──────────┘ └──────────┘            │     │    │   │
│  │  │  │  ┌──────────┐ ┌──────────┐ ┌──────────┐            │     │    │   │
│  │  │  │  │transactions│ │ rentals │ │ coupons │            │     │    │   │
│  │  │  │  └──────────┘ └──────────┘ └──────────┘            │     │    │   │
│  │  │  └────────────────────────────────────────────────────┘     │    │   │
│  │  └─────────────────────────────────────────────────────────────┘    │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 Design Patterns Used

1. **MVC Pattern**: Separation of Model, View, Controller
2. **Repository Pattern**: Data access abstraction
3. **Service Layer Pattern**: Business logic encapsulation
4. **Factory Pattern**: Application and object creation
5. **Singleton Pattern**: Database connection, configuration
6. **Strategy Pattern**: Different transaction processors

---

## 3. Architecture Comparison Table

| Aspect | Legacy System | Reengineered System |
|--------|---------------|---------------------|
| **Architecture Style** | Monolithic Desktop | Layered Web MVC |
| **UI Technology** | Java Swing | HTML5 + Bootstrap + Jinja2 |
| **UI Accessibility** | Single Machine | Any Device with Browser |
| **Backend Language** | Java | Python |
| **Backend Framework** | None (raw Java) | Flask |
| **Data Storage** | Plain Text Files | SQLite/PostgreSQL |
| **ORM** | None | SQLAlchemy |
| **Authentication** | Plain Text Comparison | PBKDF2 Hashing + Sessions |
| **Session Management** | JFrame State | Flask-Login |
| **API Support** | None | REST API Endpoints |
| **Configuration** | Hardcoded | Environment-based Config |
| **Error Handling** | Basic Try-Catch | Centralized Exception Handling |
| **Logging** | Console.println | Python Logging Module |
| **Testing** | Minimal | pytest with Fixtures |
| **Concurrency** | Single-threaded | Multi-user Support |
| **Deployment** | Manual JAR | Docker/Cloud Ready |
| **Version Control** | Basic | Git with Branching |
| **Documentation** | Minimal | Comprehensive |

---

## 4. Layer Responsibilities

### 4.1 Presentation Layer

**Purpose**: Handle HTTP requests/responses, render views

**Components**:
- Controllers (Route Handlers)
- Jinja2 Templates
- Static Assets (CSS, JS)

**Responsibilities**:
- Request validation
- User authentication checks
- Response formatting
- View rendering

### 4.2 Business Logic Layer

**Purpose**: Encapsulate business rules and workflows

**Components**:
- Services
- Value Objects
- Business Exceptions

**Responsibilities**:
- Transaction processing
- Business rule validation
- Workflow orchestration
- Cross-cutting concerns

### 4.3 Data Access Layer

**Purpose**: Abstract database operations

**Components**:
- Repositories
- ORM Models
- Query Builders

**Responsibilities**:
- CRUD operations
- Query optimization
- Transaction management
- Data mapping

### 4.4 Database Layer

**Purpose**: Persistent data storage

**Components**:
- SQLite/PostgreSQL
- Migrations
- Indexes

**Responsibilities**:
- Data persistence
- Referential integrity
- Query execution
- Backup/Recovery

---

## 5. Data Flow Diagrams

### 5.1 Sale Transaction Flow

```
┌────────┐      ┌────────────┐      ┌─────────────┐      ┌────────────┐
│ Client │ ───► │ Controller │ ───► │   Service   │ ───► │ Repository │
│(Browser│      │(cashier_   │      │(transaction_│      │(item_      │
│       )│      │controller) │      │ service)    │      │repository) │
└────────┘      └────────────┘      └─────────────┘      └────────────┘
    │                 │                    │                    │
    │   POST /sale    │                    │                    │
    │   {items: [...]}│                    │                    │
    │ ───────────────►│                    │                    │
    │                 │ validate_request() │                    │
    │                 │ ──────────────────►│                    │
    │                 │                    │ process_sale()     │
    │                 │                    │ ──────────────────►│
    │                 │                    │                    │ get_items()
    │                 │                    │                    │ ──────────►
    │                 │                    │                    │ ◄──────────
    │                 │                    │ calculate_total()  │
    │                 │                    │ ──────────────────►│
    │                 │                    │                    │ update_qty()
    │                 │                    │                    │ ──────────►
    │                 │                    │                    │ ◄──────────
    │                 │                    │ save_transaction() │
    │                 │                    │ ──────────────────►│
    │                 │                    │                    │ commit()
    │                 │                    │                    │ ──────────►
    │                 │                    │◄───────────────────│ ◄──────────
    │                 │◄───────────────────│                    │
    │ ◄───────────────│                    │                    │
    │  {receipt: ...} │                    │                    │
    │                 │                    │                    │
```

### 5.2 Authentication Flow

```
┌────────┐      ┌────────────┐      ┌─────────────┐      ┌────────────┐
│ Client │ ───► │ Controller │ ───► │   Service   │ ───► │ Repository │
│        │      │(auth_      │      │(auth_       │      │(employee_  │
│        │      │controller) │      │ service)    │      │repository) │
└────────┘      └────────────┘      └─────────────┘      └────────────┘
    │                 │                    │                    │
    │  POST /login    │                    │                    │
    │  {user, pass}   │                    │                    │
    │ ───────────────►│                    │                    │
    │                 │   authenticate()   │                    │
    │                 │ ──────────────────►│                    │
    │                 │                    │  find_by_username()│
    │                 │                    │ ──────────────────►│
    │                 │                    │                    │
    │                 │                    │◄───────────────────│
    │                 │                    │ verify_password()  │
    │                 │                    │ ─────────┐         │
    │                 │                    │◄─────────┘         │
    │                 │                    │  login_user()      │
    │                 │                    │ ─────────┐         │
    │                 │                    │◄─────────┘         │
    │                 │◄───────────────────│                    │
    │ ◄───────────────│ redirect(role)     │                    │
    │                 │                    │                    │
```

---

## 6. Database Schema

### 6.1 Entity Relationship Diagram

```
┌──────────────────┐       ┌──────────────────┐
│    employees     │       │      items       │
├──────────────────┤       ├──────────────────┤
│ PK id            │       │ PK id            │
│    username      │       │    name          │
│    password_hash │       │    price         │
│    name          │       │    quantity      │
│    role          │       │    item_type     │
│    created_at    │       │    created_at    │
│    last_login    │       └────────┬─────────┘
└────────┬─────────┘                │
         │                          │
         │ 1                        │ 1
         │                          │
         ▼ M                        ▼ M
┌──────────────────┐       ┌──────────────────┐
│   transactions   │       │transaction_items │
├──────────────────┤       ├──────────────────┤
│ PK id            │       │ PK id            │
│ FK employee_id   │──┐    │ FK transaction_id│
│ FK customer_id   │  │    │ FK item_id       │───┘
│    type          │  │    │    quantity      │
│    subtotal      │  │    │    unit_price    │
│    discount      │  │    └──────────────────┘
│    tax           │  │
│    total         │  │
│    payment_method│  │
│    created_at    │  │
└────────┬─────────┘  │
         │            │
         │ M          │
         ▼ 1          │
┌──────────────────┐  │
│    customers     │  │
├──────────────────┤  │
│ PK id            │  │
│    phone         │  │
│    name          │  │
│    created_at    │  │
└────────┬─────────┘  │
         │            │
         │ 1          │
         │            │
         ▼ M          │
┌──────────────────┐  │
│     rentals      │  │
├──────────────────┤  │
│ PK id            │◄─┘
│ FK customer_id   │
│ FK item_id       │
│ FK transaction_id│
│    rental_date   │
│    due_date      │
│    returned      │
│    return_date   │
│    late_fee      │
└──────────────────┘

┌──────────────────┐
│     coupons      │
├──────────────────┤
│ PK id            │
│    code          │
│    discount_pct  │
│    is_active     │
│    created_at    │
│    expires_at    │
└──────────────────┘
```

---

## 7. Improvement Justifications

### 7.1 Separation of Concerns

**Legacy Issue**: GUI code mixed with business logic and data access
**Solution**: Layered architecture with distinct responsibilities
**Benefit**: Each layer can be modified independently, easier testing

### 7.2 Data Integrity

**Legacy Issue**: Text files have no transaction support, data can corrupt
**Solution**: SQLite/PostgreSQL with ACID transactions
**Benefit**: Guaranteed data consistency, rollback support

### 7.3 Security

**Legacy Issue**: Plain text passwords, no session management
**Solution**: PBKDF2 password hashing, Flask-Login sessions
**Benefit**: Industry-standard security practices

### 7.4 Scalability

**Legacy Issue**: Single user, single machine
**Solution**: Web-based with database backend
**Benefit**: Multiple concurrent users, can scale horizontally

### 7.5 Maintainability

**Legacy Issue**: High coupling, code duplication
**Solution**: Repository pattern, service layer, clean separation
**Benefit**: Changes isolated to specific layers, easier maintenance

### 7.6 Testability

**Legacy Issue**: GUI tightly coupled, hard to test
**Solution**: Dependency injection, mockable services
**Benefit**: High test coverage possible, TDD friendly

### 7.7 Accessibility

**Legacy Issue**: Requires Java installation, desktop only
**Solution**: Web-based, browser access
**Benefit**: Access from any device with a browser
