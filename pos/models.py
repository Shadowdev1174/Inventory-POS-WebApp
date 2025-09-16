from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from inventory.models import Product
from decimal import Decimal


class Sale(models.Model):
    PAYMENT_METHODS = [
        ('CASH', 'Cash'),
        ('CARD', 'Credit/Debit Card'),
        ('CHECK', 'Check'),
        ('MOBILE', 'Mobile Payment'),
    ]

    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
        ('REFUNDED', 'Refunded'),
    ]

    sale_number = models.CharField(max_length=20, unique=True)
    cashier = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sales')
    
    # Amounts
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Payment info
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, default='CASH')
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    change_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Status and timestamps
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Sale #{self.sale_number}"

    @property
    def change_due(self):
        return self.amount_paid - self.total_amount

    def save(self, *args, **kwargs):
        if not self.sale_number:
            # Generate sale number
            last_sale = Sale.objects.order_by('-id').first()
            if last_sale:
                last_number = int(last_sale.sale_number.split('-')[-1])
                self.sale_number = f"INV-{last_number + 1:06d}"
            else:
                self.sale_number = "INV-000001"
        
        # Calculate change
        self.change_amount = self.amount_paid - self.total_amount
        
        super().save(*args, **kwargs)


class SaleItem(models.Model):
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    class Meta:
        unique_together = ['sale', 'product']

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"

    @property
    def line_total(self):
        return (self.unit_price * self.quantity) - self.discount

    def save(self, *args, **kwargs):
        # Set unit price from product if not provided
        if not self.unit_price:
            self.unit_price = self.product.selling_price
        super().save(*args, **kwargs)


class Cart(models.Model):
    """Temporary cart for POS system"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'product']

    def __str__(self):
        return f"{self.user.username} - {self.product.name} x {self.quantity}"

    @property
    def line_total(self):
        return self.product.selling_price * self.quantity


class PaymentRecord(models.Model):
    """Track individual payments for a sale (for split payments)"""
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name='payments')
    payment_method = models.CharField(max_length=20, choices=Sale.PAYMENT_METHODS)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    reference_number = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sale.sale_number} - {self.payment_method} - ₱{self.amount}"


class Refund(models.Model):
    REFUND_REASONS = [
        ('DEFECTIVE', 'Defective Product'),
        ('WRONG_ITEM', 'Wrong Item'),
        ('CUSTOMER_REQUEST', 'Customer Request'),
        ('DAMAGED', 'Damaged in Transit'),
        ('OTHER', 'Other'),
    ]

    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name='refunds')
    sale_item = models.ForeignKey(SaleItem, on_delete=models.CASCADE, related_name='refunds')
    quantity_refunded = models.PositiveIntegerField()
    refund_amount = models.DecimalField(max_digits=10, decimal_places=2)
    reason = models.CharField(max_length=20, choices=REFUND_REASONS)
    notes = models.TextField(blank=True)
    processed_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Refund for {self.sale.sale_number} - {self.sale_item.product.name}"
