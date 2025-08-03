from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from enum import Enum


# Enums for transaction types and statuses
class TransactionType(str, Enum):
    PURCHASE = "purchase"
    SALE = "sale"


class PaymentStatus(str, Enum):
    PENDING = "pending"
    PARTIAL = "partial"
    PAID = "paid"
    OVERDUE = "overdue"


class PaymentType(str, Enum):
    CASH = "cash"
    BANK_TRANSFER = "bank_transfer"
    CREDIT_CARD = "credit_card"
    CHECK = "check"


# Product/Inventory Management
class Product(SQLModel, table=True):
    __tablename__ = "products"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    code: str = Field(unique=True, max_length=50, index=True)
    name: str = Field(max_length=200)
    description: str = Field(default="", max_length=1000)
    unit: str = Field(max_length=20)  # pcs, kg, liter, etc.
    purchase_price: Decimal = Field(decimal_places=2, ge=0)
    selling_price: Decimal = Field(decimal_places=2, ge=0)
    stock_quantity: Decimal = Field(default=Decimal("0"), decimal_places=2, ge=0)
    minimum_stock: Decimal = Field(default=Decimal("0"), decimal_places=2, ge=0)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    purchase_items: List["PurchaseItem"] = Relationship(back_populates="product")
    sale_items: List["SaleItem"] = Relationship(back_populates="product")
    stock_movements: List["StockMovement"] = Relationship(back_populates="product")


# Customer Management
class Customer(SQLModel, table=True):
    __tablename__ = "customers"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    code: str = Field(unique=True, max_length=50, index=True)
    name: str = Field(max_length=200)
    email: Optional[str] = Field(default=None, max_length=255)
    phone: Optional[str] = Field(default=None, max_length=20)
    address: str = Field(default="", max_length=500)
    credit_limit: Decimal = Field(default=Decimal("0"), decimal_places=2, ge=0)
    current_balance: Decimal = Field(default=Decimal("0"), decimal_places=2)  # Outstanding receivables
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    sales: List["Sale"] = Relationship(back_populates="customer")
    receivable_payments: List["ReceivablePayment"] = Relationship(back_populates="customer")


# Supplier Management
class Supplier(SQLModel, table=True):
    __tablename__ = "suppliers"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    code: str = Field(unique=True, max_length=50, index=True)
    name: str = Field(max_length=200)
    email: Optional[str] = Field(default=None, max_length=255)
    phone: Optional[str] = Field(default=None, max_length=20)
    address: str = Field(default="", max_length=500)
    current_balance: Decimal = Field(default=Decimal("0"), decimal_places=2)  # Outstanding payables
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    purchases: List["Purchase"] = Relationship(back_populates="supplier")
    payable_payments: List["PayablePayment"] = Relationship(back_populates="supplier")


# Purchase Transaction from Suppliers
class Purchase(SQLModel, table=True):
    __tablename__ = "purchases"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    invoice_number: str = Field(unique=True, max_length=100, index=True)
    supplier_id: int = Field(foreign_key="suppliers.id")
    transaction_date: datetime = Field(default_factory=datetime.utcnow, index=True)
    due_date: Optional[datetime] = Field(default=None, index=True)
    subtotal: Decimal = Field(decimal_places=2, ge=0)
    tax_amount: Decimal = Field(default=Decimal("0"), decimal_places=2, ge=0)
    discount_amount: Decimal = Field(default=Decimal("0"), decimal_places=2, ge=0)
    total_amount: Decimal = Field(decimal_places=2, ge=0)
    paid_amount: Decimal = Field(default=Decimal("0"), decimal_places=2, ge=0)
    payment_status: PaymentStatus = Field(default=PaymentStatus.PENDING)
    notes: str = Field(default="", max_length=1000)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    supplier: Supplier = Relationship(back_populates="purchases")
    purchase_items: List["PurchaseItem"] = Relationship(back_populates="purchase")
    payable_payments: List["PayablePayment"] = Relationship(back_populates="purchase")


class PurchaseItem(SQLModel, table=True):
    __tablename__ = "purchase_items"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    purchase_id: int = Field(foreign_key="purchases.id")
    product_id: int = Field(foreign_key="products.id")
    quantity: Decimal = Field(decimal_places=2, gt=0)
    unit_price: Decimal = Field(decimal_places=2, ge=0)
    discount_amount: Decimal = Field(default=Decimal("0"), decimal_places=2, ge=0)
    total_amount: Decimal = Field(decimal_places=2, ge=0)

    # Relationships
    purchase: Purchase = Relationship(back_populates="purchase_items")
    product: Product = Relationship(back_populates="purchase_items")


# Sales Transaction to Customers
class Sale(SQLModel, table=True):
    __tablename__ = "sales"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    invoice_number: str = Field(unique=True, max_length=100, index=True)
    customer_id: int = Field(foreign_key="customers.id")
    transaction_date: datetime = Field(default_factory=datetime.utcnow, index=True)
    due_date: Optional[datetime] = Field(default=None, index=True)
    subtotal: Decimal = Field(decimal_places=2, ge=0)
    tax_amount: Decimal = Field(default=Decimal("0"), decimal_places=2, ge=0)
    discount_amount: Decimal = Field(default=Decimal("0"), decimal_places=2, ge=0)
    total_amount: Decimal = Field(decimal_places=2, ge=0)
    paid_amount: Decimal = Field(default=Decimal("0"), decimal_places=2, ge=0)
    payment_status: PaymentStatus = Field(default=PaymentStatus.PENDING)
    notes: str = Field(default="", max_length=1000)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    customer: Customer = Relationship(back_populates="sales")
    sale_items: List["SaleItem"] = Relationship(back_populates="sale")
    receivable_payments: List["ReceivablePayment"] = Relationship(back_populates="sale")


class SaleItem(SQLModel, table=True):
    __tablename__ = "sale_items"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    sale_id: int = Field(foreign_key="sales.id")
    product_id: int = Field(foreign_key="products.id")
    quantity: Decimal = Field(decimal_places=2, gt=0)
    unit_price: Decimal = Field(decimal_places=2, ge=0)
    discount_amount: Decimal = Field(default=Decimal("0"), decimal_places=2, ge=0)
    total_amount: Decimal = Field(decimal_places=2, ge=0)

    # Relationships
    sale: Sale = Relationship(back_populates="sale_items")
    product: Product = Relationship(back_populates="sale_items")


# Stock Movement Tracking
class StockMovement(SQLModel, table=True):
    __tablename__ = "stock_movements"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    product_id: int = Field(foreign_key="products.id")
    transaction_type: TransactionType
    reference_id: int  # ID of purchase or sale
    reference_number: str = Field(max_length=100)  # Invoice number
    quantity_in: Decimal = Field(default=Decimal("0"), decimal_places=2, ge=0)
    quantity_out: Decimal = Field(default=Decimal("0"), decimal_places=2, ge=0)
    balance_after: Decimal = Field(decimal_places=2, ge=0)
    unit_cost: Decimal = Field(decimal_places=2, ge=0)
    notes: str = Field(default="", max_length=500)
    movement_date: datetime = Field(default_factory=datetime.utcnow, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    product: Product = Relationship(back_populates="stock_movements")


# Payment Management for Supplier Debts (Accounts Payable)
class PayablePayment(SQLModel, table=True):
    __tablename__ = "payable_payments"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    payment_number: str = Field(unique=True, max_length=100, index=True)
    supplier_id: int = Field(foreign_key="suppliers.id")
    purchase_id: Optional[int] = Field(default=None, foreign_key="purchases.id")
    payment_date: datetime = Field(default_factory=datetime.utcnow, index=True)
    payment_amount: Decimal = Field(decimal_places=2, gt=0)
    payment_type: PaymentType = Field(default=PaymentType.CASH)
    reference_number: str = Field(default="", max_length=100)  # Check number, transfer ref, etc.
    notes: str = Field(default="", max_length=500)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    supplier: Supplier = Relationship(back_populates="payable_payments")
    purchase: Optional[Purchase] = Relationship(back_populates="payable_payments")


# Payment Management for Customer Receivables (Accounts Receivable)
class ReceivablePayment(SQLModel, table=True):
    __tablename__ = "receivable_payments"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    payment_number: str = Field(unique=True, max_length=100, index=True)
    customer_id: int = Field(foreign_key="customers.id")
    sale_id: Optional[int] = Field(default=None, foreign_key="sales.id")
    payment_date: datetime = Field(default_factory=datetime.utcnow, index=True)
    payment_amount: Decimal = Field(decimal_places=2, gt=0)
    payment_type: PaymentType = Field(default=PaymentType.CASH)
    reference_number: str = Field(default="", max_length=100)  # Check number, transfer ref, etc.
    notes: str = Field(default="", max_length=500)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    customer: Customer = Relationship(back_populates="receivable_payments")
    sale: Optional[Sale] = Relationship(back_populates="receivable_payments")


# Non-persistent schemas for validation and forms


class ProductCreate(SQLModel, table=False):
    code: str = Field(max_length=50)
    name: str = Field(max_length=200)
    description: str = Field(default="", max_length=1000)
    unit: str = Field(max_length=20)
    purchase_price: Decimal = Field(decimal_places=2, ge=0)
    selling_price: Decimal = Field(decimal_places=2, ge=0)
    minimum_stock: Decimal = Field(default=Decimal("0"), decimal_places=2, ge=0)


class ProductUpdate(SQLModel, table=False):
    name: Optional[str] = Field(default=None, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    unit: Optional[str] = Field(default=None, max_length=20)
    purchase_price: Optional[Decimal] = Field(default=None, decimal_places=2, ge=0)
    selling_price: Optional[Decimal] = Field(default=None, decimal_places=2, ge=0)
    minimum_stock: Optional[Decimal] = Field(default=None, decimal_places=2, ge=0)
    is_active: Optional[bool] = Field(default=None)


class CustomerCreate(SQLModel, table=False):
    code: str = Field(max_length=50)
    name: str = Field(max_length=200)
    email: Optional[str] = Field(default=None, max_length=255)
    phone: Optional[str] = Field(default=None, max_length=20)
    address: str = Field(default="", max_length=500)
    credit_limit: Decimal = Field(default=Decimal("0"), decimal_places=2, ge=0)


class CustomerUpdate(SQLModel, table=False):
    name: Optional[str] = Field(default=None, max_length=200)
    email: Optional[str] = Field(default=None, max_length=255)
    phone: Optional[str] = Field(default=None, max_length=20)
    address: Optional[str] = Field(default=None, max_length=500)
    credit_limit: Optional[Decimal] = Field(default=None, decimal_places=2, ge=0)
    is_active: Optional[bool] = Field(default=None)


class SupplierCreate(SQLModel, table=False):
    code: str = Field(max_length=50)
    name: str = Field(max_length=200)
    email: Optional[str] = Field(default=None, max_length=255)
    phone: Optional[str] = Field(default=None, max_length=20)
    address: str = Field(default="", max_length=500)


class SupplierUpdate(SQLModel, table=False):
    name: Optional[str] = Field(default=None, max_length=200)
    email: Optional[str] = Field(default=None, max_length=255)
    phone: Optional[str] = Field(default=None, max_length=20)
    address: Optional[str] = Field(default=None, max_length=500)
    is_active: Optional[bool] = Field(default=None)


class PurchaseItemCreate(SQLModel, table=False):
    product_id: int
    quantity: Decimal = Field(decimal_places=2, gt=0)
    unit_price: Decimal = Field(decimal_places=2, ge=0)
    discount_amount: Decimal = Field(default=Decimal("0"), decimal_places=2, ge=0)


class PurchaseCreate(SQLModel, table=False):
    invoice_number: str = Field(max_length=100)
    supplier_id: int
    transaction_date: datetime
    due_date: Optional[datetime] = Field(default=None)
    tax_amount: Decimal = Field(default=Decimal("0"), decimal_places=2, ge=0)
    discount_amount: Decimal = Field(default=Decimal("0"), decimal_places=2, ge=0)
    notes: str = Field(default="", max_length=1000)
    items: List[PurchaseItemCreate]


class SaleItemCreate(SQLModel, table=False):
    product_id: int
    quantity: Decimal = Field(decimal_places=2, gt=0)
    unit_price: Decimal = Field(decimal_places=2, ge=0)
    discount_amount: Decimal = Field(default=Decimal("0"), decimal_places=2, ge=0)


class SaleCreate(SQLModel, table=False):
    invoice_number: str = Field(max_length=100)
    customer_id: int
    transaction_date: datetime
    due_date: Optional[datetime] = Field(default=None)
    tax_amount: Decimal = Field(default=Decimal("0"), decimal_places=2, ge=0)
    discount_amount: Decimal = Field(default=Decimal("0"), decimal_places=2, ge=0)
    notes: str = Field(default="", max_length=1000)
    items: List[SaleItemCreate]


class PayablePaymentCreate(SQLModel, table=False):
    payment_number: str = Field(max_length=100)
    supplier_id: int
    purchase_id: Optional[int] = Field(default=None)
    payment_date: datetime
    payment_amount: Decimal = Field(decimal_places=2, gt=0)
    payment_type: PaymentType = Field(default=PaymentType.CASH)
    reference_number: str = Field(default="", max_length=100)
    notes: str = Field(default="", max_length=500)


class ReceivablePaymentCreate(SQLModel, table=False):
    payment_number: str = Field(max_length=100)
    customer_id: int
    sale_id: Optional[int] = Field(default=None)
    payment_date: datetime
    payment_amount: Decimal = Field(decimal_places=2, gt=0)
    payment_type: PaymentType = Field(default=PaymentType.CASH)
    reference_number: str = Field(default="", max_length=100)
    notes: str = Field(default="", max_length=500)


# Report schemas for data presentation
class StockReportItem(SQLModel, table=False):
    product_code: str
    product_name: str
    movement_date: datetime
    reference_number: str
    transaction_type: str
    quantity_in: Decimal
    quantity_out: Decimal
    balance_after: Decimal
    unit_cost: Decimal


class PayableReportItem(SQLModel, table=False):
    supplier_code: str
    supplier_name: str
    invoice_number: str
    transaction_date: datetime
    due_date: Optional[datetime]
    total_amount: Decimal
    paid_amount: Decimal
    outstanding_amount: Decimal
    payment_status: PaymentStatus


class ReceivableReportItem(SQLModel, table=False):
    customer_code: str
    customer_name: str
    invoice_number: str
    transaction_date: datetime
    due_date: Optional[datetime]
    total_amount: Decimal
    paid_amount: Decimal
    outstanding_amount: Decimal
    payment_status: PaymentStatus
