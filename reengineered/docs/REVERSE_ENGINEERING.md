# Reverse Engineering Report

## 1. Executive Summary

This document presents the findings from the Reverse Engineering phase of the software reengineering process. The analysis recovers the design, data structures, workflows, and identifies code and data smells from the legacy POS system.

## 2. Recovered System Architecture

### 2.1 High-Level Architecture (Legacy)

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          PRESENTATION LAYER                              │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐   │
│  │ Login_       │ │ Cashier_     │ │ Admin_       │ │ Transaction_ │   │
│  │ Interface    │ │ Interface    │ │ Interface    │ │ Interface    │   │
│  └──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘   │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐   │
│  │ EnterItem_   │ │ Payment_     │ │ AddEmployee_ │ │ UpdateEmp_   │   │
│  │ Interface    │ │ Interface    │ │ Interface    │ │ Interface    │   │
│  └──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                          BUSINESS LOGIC LAYER                            │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐                    │
│  │ POSSystem    │ │ PointOfSale  │ │ Management   │                    │
│  │ (Controller) │ │ (Abstract)   │ │ (User Mgmt)  │                    │
│  └──────────────┘ └──────────────┘ └──────────────┘                    │
│         │               │                 │                              │
│         │        ┌──────┴───────┐         │                              │
│         │        ▼      ▼       ▼         │                              │
│         │     ┌─────┐┌─────┐┌─────┐       │                              │
│         │     │ POS ││ POR ││ POH │       │                              │
│         │     │Sale ││Rent ││Rtrn │       │                              │
│         │     └─────┘└─────┘└─────┘       │                              │
│         │               │                 │                              │
│         │        ┌──────┴───────┐         │                              │
│         │        ▼              │         │                              │
│         │  ┌───────────┐        │         │                              │
│         │  │ Inventory │◄───────┴─────────┤                              │
│         │  │(Singleton)│                  │                              │
│         │  └───────────┘                  │                              │
│         │        │                        │                              │
│  ┌──────┴────────┼────────────────────────┴───────┐                     │
│  │EmployeeMgmt   │                                │                     │
│  └───────────────┴────────────────────────────────┘                     │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                          DATA LAYER                                      │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐                    │
│  │ Employee     │ │ Item         │ │ ReturnItem   │                    │
│  │ (Model)      │ │ (Model)      │ │ (Model)      │                    │
│  └──────────────┘ └──────────────┘ └──────────────┘                    │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                    TEXT FILE STORAGE                             │   │
│  │  employeeDatabase.txt │ itemDatabase.txt │ userDatabase.txt     │   │
│  │  rentalDatabase.txt   │ couponNumber.txt │ saleInvoiceRecord.txt│   │
│  └─────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
```

### 2.2 Class Diagram

```
                    ┌─────────────────────┐
                    │   <<abstract>>      │
                    │    PointOfSale      │
                    ├─────────────────────┤
                    │ - totalPrice: double│
                    │ - tax: double       │
                    │ - discount: float   │
                    │ - inventory:Inventory│
                    │ - databaseItem: List│
                    │ - transactionItem:  │
                    │   List<Item>        │
                    ├─────────────────────┤
                    │ + startNew()        │
                    │ + enterItem()       │
                    │ + updateTotal()     │
                    │ + removeItems()     │
                    │ + coupon()          │
                    │ + creditCard()      │
                    │ # detectSystem()    │
                    └─────────┬───────────┘
                              │
          ┌───────────────────┼───────────────────┐
          │                   │                   │
          ▼                   ▼                   ▼
    ┌───────────┐       ┌───────────┐       ┌───────────┐
    │    POS    │       │    POR    │       │    POH    │
    │   (Sale)  │       │  (Rental) │       │ (Returns) │
    ├───────────┤       ├───────────┤       ├───────────┤
    │           │       │ phoneNum  │       │ phone     │
    ├───────────┤       ├───────────┤       │ returnList│
    │ + endPOS()│       │ + endPOS()│       ├───────────┤
    │ +retrieve │       │ +retrieve │       │ + endPOS()│
    │  Temp()   │       │  Temp()   │       │ +retrieve │
    │ +deleteTem│       │ +deleteTem│       │  Temp()   │
    │  pItem()  │       │  pItem()  │       │ +deleteTem│
    └───────────┘       └───────────┘       │  pItem()  │
                                            └───────────┘

    ┌───────────────┐                  ┌───────────────┐
    │   Inventory   │                  │  POSSystem    │
    │ <<Singleton>> │                  ├───────────────┤
    ├───────────────┤                  │ - employees   │
    │ -uniqueInst   │                  │ - username    │
    ├───────────────┤                  │ - password    │
    │ +getInstance()│                  ├───────────────┤
    │ +accessInv()  │                  │ + logIn()     │
    │ +updateInv()  │                  │ + logOut()    │
    └───────────────┘                  │ + checkTemp() │
                                       │ +continueFrom │
    ┌───────────────┐                  │  Temp()       │
    │     Item      │                  └───────────────┘
    ├───────────────┤
    │ - itemID: int │                  ┌───────────────┐
    │ - itemName    │                  │   Employee    │
    │ - price: float│                  ├───────────────┤
    │ - amount: int │                  │ - username    │
    ├───────────────┤                  │ - name        │
    │ + getters     │                  │ - position    │
    │ + updateAmt() │                  │ - password    │
    └───────────────┘                  ├───────────────┤
                                       │ + getters     │
    ┌───────────────┐                  │ + setters     │
    │  ReturnItem   │                  └───────────────┘
    ├───────────────┤
    │ - itemID: int │
    │ -daysSinceRtn │
    ├───────────────┤
    │ + getItemID() │
    │ + getDays()   │
    └───────────────┘
```

## 3. Recovered Workflows

### 3.1 Authentication Workflow

```
┌─────────┐     ┌─────────────┐     ┌───────────┐     ┌──────────────┐
│  User   │────►│ Login_      │────►│ POSSystem │────►│ employeeDB   │
│         │     │ Interface   │     │ .logIn()  │     │ .txt         │
└─────────┘     └─────────────┘     └───────────┘     └──────────────┘
                      │                   │
                      │     ┌─────────────┴─────────────┐
                      │     │                           │
                      ▼     ▼                           ▼
               ┌─────────────────┐             ┌─────────────────┐
               │ Cashier_        │             │ Admin_          │
               │ Interface       │             │ Interface       │
               │ (role=Cashier)  │             │ (role=Admin)    │
               └─────────────────┘             └─────────────────┘
```

### 3.2 Sale Transaction Workflow

```
┌────────┐   ┌──────────────┐   ┌────────────┐   ┌─────────┐
│Cashier │──►│Transaction_  │──►│EnterItem_  │──►│ Item    │
│        │   │Interface     │   │Interface   │   │ Lookup  │
└────────┘   └──────────────┘   └────────────┘   └─────────┘
                   │                   │              │
                   │                   ▼              ▼
                   │            ┌────────────┐  ┌──────────┐
                   │            │ Add to     │◄─│Inventory │
                   │            │ Cart       │  │(Singleton)│
                   │            └────────────┘  └──────────┘
                   │                   │
                   ▼                   ▼
            ┌────────────┐      ┌────────────┐
            │ Apply      │◄─────│ End Trans  │
            │ Coupon     │      │            │
            └────────────┘      └────────────┘
                   │                   │
                   ▼                   ▼
            ┌────────────┐      ┌────────────┐
            │ Payment_   │─────►│ Update     │
            │ Interface  │      │ Inventory  │
            └────────────┘      └────────────┘
                   │                   │
                   ▼                   ▼
            ┌────────────┐      ┌────────────┐
            │ Cash/Card  │      │ Save       │
            │ Payment    │      │ Invoice    │
            └────────────┘      └────────────┘
```

### 3.3 Rental Workflow

```
┌────────┐   ┌──────────────┐   ┌──────────────┐
│Cashier │──►│Get Customer  │──►│Check/Create  │
│        │   │Phone Number  │   │Customer      │
└────────┘   └──────────────┘   └──────────────┘
                                       │
                                       ▼
            ┌──────────────┐    ┌──────────────┐
            │ Process      │◄───│Select Rental │
            │ Rental       │    │Items         │
            └──────────────┘    └──────────────┘
                   │
                   ▼
            ┌──────────────┐    ┌──────────────┐
            │ Update       │───►│Add to        │
            │ Inventory    │    │userDatabase  │
            └──────────────┘    └──────────────┘
```

### 3.4 Return Workflow

```
┌────────┐   ┌──────────────┐   ┌──────────────┐
│Cashier │──►│Select Return │──►│Rented Items  │
│        │   │Type          │   │     OR       │
└────────┘   └──────────────┘   │Unsatisfactory│
                                └──────────────┘
                   │                    │
         ┌─────────┴─────────┐          │
         ▼                   ▼          │
  ┌─────────────┐    ┌─────────────┐    │
  │Get Customer │    │Process      │◄───┘
  │Phone        │    │Return Sale  │
  └─────────────┘    └─────────────┘
         │
         ▼
  ┌─────────────┐    ┌─────────────┐
  │Check Late   │───►│Calculate    │
  │Days         │    │Late Fees    │
  └─────────────┘    └─────────────┘
         │
         ▼
  ┌─────────────┐    ┌─────────────┐
  │Process      │───►│Update       │
  │Payment      │    │userDatabase │
  └─────────────┘    └─────────────┘
```

## 4. Recovered Data Structures

### 4.1 Employee Database Schema

```
Format: ID Position FirstName LastName Password
Example: 110001 Admin Harry Larry 1

Field       Type      Description
---------   -------   -------------------------
ID          Integer   Unique employee identifier
Position    String    "Admin" or "Cashier"
FirstName   String    Employee first name
LastName    String    Employee last name
Password    String    Plain text password (INSECURE!)
```

### 4.2 Item Database Schema

```
Format: ItemID Name Price Quantity
Example: 1000 Potato 1.0 249

Field       Type      Description
---------   -------   -------------------------
ItemID      Integer   Unique item identifier
Name        String    Item name (no spaces)
Price       Float     Unit price
Quantity    Integer   Stock quantity
```

### 4.3 User/Customer Database Schema

```
Format: PhoneNumber RentalEntry1 RentalEntry2 ...
RentalEntry: ItemID,Date,ReturnedBoolean

Example: 6096515668 1000,6/30/09,true 1022,6/31/11,true

Field         Type         Description
-----------   -----------  -------------------------
PhoneNumber   Long         Customer phone (10 digits)
RentalEntry   Compound     ItemID,Date,IsReturned
```

### 4.4 Coupon Database Schema

```
Format: CouponCode (one per line)
Example: C001

Field        Type      Description
----------   -------   -------------------------
CouponCode   String    Valid coupon code (10% discount)
```

## 5. Design Patterns Identified

### 5.1 Singleton Pattern (Inventory.java)

```java
public class Inventory {
    private static Inventory uniqueInstance = null;
    
    private Inventory() {}
    
    public static synchronized Inventory getInstance() {
        if (uniqueInstance == null)
            uniqueInstance = new Inventory();
        return uniqueInstance;
    }
}
```

**Purpose**: Ensures single point of inventory access across all transactions.

### 5.2 Template Method Pattern (Implicit)

The `PointOfSale` abstract class defines the skeleton of transaction algorithms, with subclasses (POS, POR, POH) implementing specific steps.

### 5.3 Observer Pattern (Implicit/Partial)

GUI components update based on transaction state changes, though not formally implemented.

## 6. Code Smells Identified

### 6.1 Long Method

**Location**: `Management.java` - `getLatestReturnDate()`, `addRental()`, `updateRentalStatus()`

```java
// 100+ lines with complex nested loops and string parsing
public List<ReturnItem> getLatestReturnDate(Long phone) {
    // Many levels of nesting
    // Complex string splitting
    // Date parsing inline
}
```

**Impact**: Hard to understand, test, and maintain.

### 6.2 God Class

**Location**: `POSSystem.java`, `Management.java`

- Too many responsibilities
- Mix of authentication, file I/O, transaction management

### 6.3 Duplicate Code

**Location**: `POS.java`, `POR.java`, `POH.java`

```java
// Nearly identical deleteTempItem() method in all three classes
public void deleteTempItem(int id) {
    // Same 30+ lines of code repeated
}
```

### 6.4 Feature Envy

**Location**: Various Interface classes accessing model internals directly

```java
// Interface classes doing too much data manipulation
transactionItem.get(counter).getItemID()
transactionItem.get(counter).getItemName()
// etc.
```

### 6.5 Magic Numbers

**Location**: Throughout codebase

```java
private static float discount = 0.90f;  // 10% discount
public double tax = 1.06;               // 6% tax
while ((phoneNum = Long.parseLong(phone)) > 9999999999l || (phoneNum < 1000000000l))
```

### 6.6 Dead Code

**Location**: `PointOfSale.java`

```java
/*protected static int checkInt(){
    // Commented out code left in place
}*/
```

### 6.7 Comments as Deodorant

**Location**: Various files with commented-out code blocks instead of proper version control

## 7. Data Smells Identified

### 7.1 No Data Normalization

- User rental history stored as concatenated strings
- Redundant data in multiple files

### 7.2 Plain Text Passwords

```
110001 Admin Harry Larry 1
110002 Cashier Debra Cooper lehigh2016
```

**Security Risk**: Critical vulnerability

### 7.3 Inconsistent Data Formats

- Dates stored as `MM/dd/yy` strings
- Phone numbers as long integers without validation
- No referential integrity between files

### 7.4 Data Duplication

- Same phone number appears multiple times in userDatabase
- No mechanism to prevent duplicates

### 7.5 No Transaction Atomicity

- File writes can be interrupted
- No rollback mechanism
- Data corruption possible on crash

### 7.6 Scalability Issues

- Entire files read into memory
- Linear search for lookups
- No indexing

## 8. Limitations Identified

1. **Single User**: No concurrent user support
2. **No Network**: Desktop-only, single machine
3. **No Backup**: No automated backup mechanism
4. **Limited Reporting**: No sales analytics or reports
5. **No Audit Trail**: Limited logging capabilities
6. **Hardcoded Settings**: Tax rates, discounts hardcoded
7. **No Input Validation**: Potential for crashes
8. **No Error Recovery**: Poor exception handling
9. **Platform Dependent**: Windows/Unix path handling issues
10. **No API**: Cannot integrate with other systems
