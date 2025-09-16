// Fast POS JavaScript - No Flickering, Maximum Performance
document.addEventListener('DOMContentLoaded', function() {
    // Get CSRF token
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    const csrftoken = getCookie('csrftoken');

    // Simple notification system
    function showToast(message, type = 'success') {
        const toast = document.createElement('div');
        toast.className = `fixed top-4 right-4 z-50 p-3 rounded shadow-lg text-white ${
            type === 'success' ? 'bg-green-500' : 'bg-red-500'
        }`;
        toast.textContent = message;
        document.body.appendChild(toast);
        setTimeout(() => toast.remove(), 2000);
    }

    // Fast cart update without page reload
    function updateCartDisplay(data) {
        // Update cart numbers instantly
        const cartCount = document.getElementById('cart-count');
        const cartTotal = document.getElementById('cart-total');
        const cartTax = document.getElementById('cart-tax');
        const cartFinalTotal = document.getElementById('cart-final-total');
        
        if (cartCount) cartCount.textContent = data.cart_count || 0;
        if (cartTotal) cartTotal.textContent = `₱${(data.cart_total || 0).toFixed(2)}`;
        if (cartTax) cartTax.textContent = `₱${(data.cart_tax || 0).toFixed(2)}`;
        if (cartFinalTotal) cartFinalTotal.textContent = `₱${(data.cart_final_total || 0).toFixed(2)}`;

        // Enable/disable buttons
        const checkoutBtn = document.getElementById('checkout-btn');
        const clearBtn = document.getElementById('clear-cart-btn');
        
        if (data.cart_count > 0) {
            if (checkoutBtn) checkoutBtn.disabled = false;
            if (clearBtn) clearBtn.disabled = false;
        } else {
            if (checkoutBtn) checkoutBtn.disabled = true;
            if (clearBtn) clearBtn.disabled = true;
        }
    }

    // Fast AJAX request
    async function fastRequest(url, data = null) {
        try {
            const response = await fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrftoken,
                },
                body: data ? JSON.stringify(data) : null
            });
            return await response.json();
        } catch (error) {
            console.error('Request failed:', error);
            showToast('Operation failed', 'error');
            return null;
        }
    }
    const searchResults = document.getElementById('search-results');
    const productsContainer = document.getElementById('products-container');
    const cartItems = document.getElementById('cart-items');
    const cartCount = document.getElementById('cart-count');
    const cartSubtotal = document.getElementById('cart-subtotal');
    const cartTax = document.getElementById('cart-tax');
    const cartTotal = document.getElementById('cart-total');
    const checkoutBtn = document.getElementById('checkout-btn');
    const clearCartBtn = document.getElementById('clear-cart-btn');
    
    // Modals
    const checkoutModal = document.getElementById('checkout-modal');
    const successModal = document.getElementById('success-modal');
    const paymentMethod = document.getElementById('payment-method');
    const amountReceived = document.getElementById('amount-received');
    const changeAmount = document.getElementById('change-amount');

    // Product search functionality
    let searchTimeout;
    productSearch.addEventListener('input', function() {
        clearTimeout(searchTimeout);
        const query = this.value.trim();
        
        if (query.length < 2) {
            searchResults.classList.add('hidden');
            return;
        }
        
        searchTimeout = setTimeout(() => {
            fetch(`/pos/api/search/?q=${encodeURIComponent(query)}`)
                .then(response => response.json())
                .then(data => {
                    displaySearchResults(data.products);
                })
                .catch(error => {
                    console.error('Search error:', error);
                });
        }, 300);
    });

    // Display search results
    function displaySearchResults(products) {
        if (products.length === 0) {
            searchResults.innerHTML = '<div class="p-4 text-gray-500">No products found</div>';
        } else {
            searchResults.innerHTML = products.map(product => `
                <div class="search-result-item p-3 hover:bg-gray-50 cursor-pointer border-b" data-product-id="${product.id}">
                    <div class="flex items-center space-x-3">
                        ${product.image ? 
                            `<img src="${product.image}" alt="${product.name}" class="w-10 h-10 object-cover rounded">` :
                            `<div class="w-10 h-10 bg-gray-200 rounded flex items-center justify-center">
                                <i class="fas fa-box text-gray-400"></i>
                            </div>`
                        }
                        <div class="flex-1">
                            <div class="font-medium">${product.name}</div>
                            <div class="text-sm text-gray-500">${product.category} - Stock: ${product.stock}</div>
                        </div>
                        <div class="text-blue-600 font-bold">₱${product.price}</div>
                    </div>
                </div>
            `).join('');
        }
        searchResults.classList.remove('hidden');
    }

    // Handle search result clicks
    searchResults.addEventListener('click', function(e) {
        const item = e.target.closest('.search-result-item');
        if (item) {
            const productId = item.dataset.productId;
            addToCart(productId);
            productSearch.value = '';
            searchResults.classList.add('hidden');
        }
    });

    // Hide search results when clicking outside
    document.addEventListener('click', function(e) {
        if (!productSearch.contains(e.target) && !searchResults.contains(e.target)) {
            searchResults.classList.add('hidden');
        }
    });

    // Category filtering
    const categoryFilters = document.querySelectorAll('.category-filter');
    categoryFilters.forEach(filter => {
        filter.addEventListener('click', function() {
            // Update active state
            categoryFilters.forEach(f => f.classList.remove('active', 'bg-blue-600', 'text-white'));
            categoryFilters.forEach(f => f.classList.add('bg-gray-200', 'text-gray-700'));
            
            this.classList.add('active', 'bg-blue-600', 'text-white');
            this.classList.remove('bg-gray-200', 'text-gray-700');
            
            // Filter products
            const category = this.dataset.category;
            const productCards = document.querySelectorAll('.product-card');
            
            productCards.forEach(card => {
                if (category === 'all' || card.dataset.category === category) {
                    card.style.display = 'block';
                } else {
                    card.style.display = 'none';
                }
            });
        });
    });

    // Product card clicks
    productsContainer.addEventListener('click', function(e) {
        const productCard = e.target.closest('.product-card');
        if (productCard) {
            const productId = productCard.dataset.productId;
            addToCart(productId);
        }
    });

    // Add to cart function
    function addToCart(productId, quantity = 1) {
        fetch('/pos/add-to-cart/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken
            },
            body: JSON.stringify({
                product_id: productId,
                quantity: quantity
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                // Update cart display smoothly without page reload
                updateCartDisplay(data);
                showNotification(data.message, 'success');
                // Refresh cart items via AJAX instead of page reload
                refreshCartItems();
            } else {
                showNotification(data.message, 'error');
            }
        })
        .catch(error => {
            console.error('Add to cart error:', error);
            showNotification('Error adding product to cart', 'error');
        });
    }

    // Update cart display
    function updateCartDisplay(data) {
        cartCount.textContent = data.cart_count;
        cartSubtotal.textContent = `₱${data.cart_total.toFixed(2)}`;
        cartTax.textContent = `₱${data.cart_tax.toFixed(2)}`;
        cartTotal.textContent = `$${data.cart_final_total.toFixed(2)}`;
        
        // Enable/disable buttons
        const hasItems = data.cart_count > 0;
        checkoutBtn.disabled = !hasItems;
        clearCartBtn.disabled = !hasItems;
        
        if (hasItems) {
            checkoutBtn.classList.remove('bg-gray-300', 'cursor-not-allowed');
            checkoutBtn.classList.add('bg-green-600', 'hover:bg-green-700');
            clearCartBtn.classList.remove('bg-gray-300', 'cursor-not-allowed');
            clearCartBtn.classList.add('bg-red-600', 'hover:bg-red-700');
        } else {
            checkoutBtn.classList.add('bg-gray-300', 'cursor-not-allowed');
            checkoutBtn.classList.remove('bg-green-600', 'hover:bg-green-700');
            clearCartBtn.classList.add('bg-gray-300', 'cursor-not-allowed');
            clearCartBtn.classList.remove('bg-red-600', 'hover:bg-red-700');
        }
        
        // Refresh cart items smoothly without page reload
        if (data.refresh_cart) {
            refreshCartItems();
        }
    }

    // Cart quantity controls
    cartItems.addEventListener('click', function(e) {
        const cartId = e.target.closest('.cart-item')?.dataset.cartId;
        if (!cartId) return;

        if (e.target.closest('.quantity-btn.minus')) {
            updateCartQuantity(cartId, 'decrease');
        } else if (e.target.closest('.quantity-btn.plus')) {
            updateCartQuantity(cartId, 'increase');
        } else if (e.target.closest('.remove-item')) {
            removeFromCart(cartId);
        }
    });

    // Update cart quantity
    function updateCartQuantity(cartId, action) {
        const cartItem = document.querySelector(`[data-cart-id="${cartId}"]`);
        const quantitySpan = cartItem.querySelector('.quantity');
        let currentQuantity = parseInt(quantitySpan.textContent);
        
        if (action === 'increase') {
            currentQuantity++;
        } else if (action === 'decrease') {
            currentQuantity--;
        }
        
        if (currentQuantity <= 0) {
            removeFromCart(cartId);
            return;
        }
        
        fetch('/pos/update-cart/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken
            },
            body: JSON.stringify({
                cart_id: cartId,
                quantity: currentQuantity
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                quantitySpan.textContent = currentQuantity;
                updateCartDisplay(data);
            } else {
                showNotification(data.message, 'error');
            }
        })
        .catch(error => {
            console.error('Update cart error:', error);
            showNotification('Error updating cart', 'error');
        });
    }

    // Remove from cart
    function removeFromCart(cartId) {
        fetch('/pos/remove-from-cart/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken
            },
            body: JSON.stringify({
                cart_id: cartId
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                document.querySelector(`[data-cart-id="${cartId}"]`).remove();
                updateCartDisplay(data);
                showNotification(data.message, 'success');
                
                // Show empty cart message if no items
                if (data.cart_count === 0) {
                    cartItems.innerHTML = `
                        <div id="empty-cart" class="text-center py-8">
                            <i class="fas fa-shopping-cart text-gray-300 text-4xl mb-3"></i>
                            <p class="text-gray-500">Cart is empty</p>
                            <p class="text-sm text-gray-400">Add products to start selling</p>
                        </div>
                    `;
                }
            } else {
                showNotification(data.message, 'error');
            }
        })
        .catch(error => {
            console.error('Remove from cart error:', error);
            showNotification('Error removing item from cart', 'error');
        });
    }

    // Clear cart
    clearCartBtn.addEventListener('click', function() {
        if (confirm('Are you sure you want to clear the cart?')) {
            fetch('/pos/clear-cart/', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrftoken
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    // Update cart display smoothly instead of page reload
                    updateCartDisplay(data);
                    showNotification('Cart cleared successfully', 'success');
                    clearCartItemsDisplay();
                } else {
                    showNotification(data.message, 'error');
                }
            })
            .catch(error => {
                console.error('Clear cart error:', error);
                showNotification('Error clearing cart', 'error');
            });
        }
    });

    // Checkout process
    checkoutBtn.addEventListener('click', function() {
        const total = parseFloat(cartTotal.textContent.replace('$', ''));
        document.getElementById('checkout-total').textContent = `$${total.toFixed(2)}`;
        checkoutModal.classList.remove('hidden');
    });

    // Payment method change
    paymentMethod.addEventListener('change', function() {
        const cashPayment = document.getElementById('cash-payment');
        if (this.value === 'cash') {
            cashPayment.style.display = 'block';
        } else {
            cashPayment.style.display = 'none';
            changeAmount.classList.add('hidden');
        }
    });

    // Amount received input with real-time validation
    amountReceived.addEventListener('input', function() {
        const total = parseFloat(document.getElementById('checkout-total').textContent.replace('$', ''));
        const received = parseFloat(this.value) || 0;
        const change = received - total;
        
        // Reset styling
        this.classList.remove('border-red-500', 'border-green-500', 'border-yellow-500');
        this.classList.add('border-gray-300');
        
        if (this.value === '' || received === 0) {
            // Empty or zero - neutral state
            changeAmount.classList.add('hidden');
        } else if (received < total) {
            // Insufficient amount - red border
            this.classList.remove('border-gray-300');
            this.classList.add('border-red-500');
            changeAmount.classList.add('hidden');
        } else if (received >= total) {
            // Sufficient amount - green border
            this.classList.remove('border-gray-300');
            this.classList.add('border-green-500');
            changeAmount.classList.remove('hidden');
            changeAmount.querySelector('span').textContent = `$${change.toFixed(2)}`;
        }
    });

    // Cancel checkout
    document.getElementById('cancel-checkout').addEventListener('click', function() {
        checkoutModal.classList.add('hidden');
        amountReceived.value = '';
        changeAmount.classList.add('hidden');
    });

    // Confirm payment
    document.getElementById('confirm-payment').addEventListener('click', function() {
        const total = parseFloat(document.getElementById('checkout-total').textContent.replace('$', ''));
        const method = paymentMethod.value;
        let amountPaid = total;
        
        // Reset input styling
        amountReceived.classList.remove('border-red-500', 'border-green-500');
        amountReceived.classList.add('border-gray-300');
        
        if (method === 'cash') {
            const inputAmount = parseFloat(amountReceived.value) || 0;
            
            // Enhanced validation for cash payments
            if (inputAmount <= 0) {
                amountReceived.classList.remove('border-gray-300');
                amountReceived.classList.add('border-red-500');
                showNotification('Please enter a valid cash amount', 'error');
                amountReceived.focus();
                return;
            }
            
            if (inputAmount < total) {
                const shortage = total - inputAmount;
                amountReceived.classList.remove('border-gray-300');
                amountReceived.classList.add('border-red-500');
                showNotification(`Insufficient cash. Short by $${shortage.toFixed(2)}`, 'error');
                amountReceived.focus();
                return;
            }
            
            // Valid amount - show green border
            amountReceived.classList.remove('border-gray-300', 'border-red-500');
            amountReceived.classList.add('border-green-500');
            amountPaid = inputAmount;
        }
        
        // Process checkout
        fetch('/pos/checkout/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken
            },
            body: JSON.stringify({
                payment_method: method,
                amount_paid: amountPaid
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                checkoutModal.classList.add('hidden');
                showSuccessModal(data);
            } else {
                // Enhanced error handling for different error types
                if (data.error_type === 'insufficient_cash') {
                    // Focus on the amount input for cash shortage
                    amountReceived.focus();
                    amountReceived.select();
                    showNotification(data.message, 'error');
                } else if (data.error_type === 'invalid_amount') {
                    // Focus on the amount input for invalid amount
                    amountReceived.focus();
                    showNotification(data.message, 'error');
                } else {
                    // General error handling
                    showNotification(data.message, 'error');
                }
            }
        })
        .catch(error => {
            console.error('Checkout error:', error);
            showNotification('Error processing payment. Please try again.', 'error');
        });
    });

    // Show success modal
    function showSuccessModal(data) {
        document.getElementById('sale-number').textContent = data.sale_number;
        document.getElementById('sale-total').textContent = `$${data.total_amount.toFixed(2)}`;
        
        if (data.change_amount > 0) {
            document.getElementById('sale-change').classList.remove('hidden');
            document.getElementById('change-given').textContent = `$${data.change_amount.toFixed(2)}`;
        }
        
        successModal.classList.remove('hidden');
    }

    // New sale
    document.getElementById('new-sale').addEventListener('click', function() {
        // Clear cart display and reset POS instead of page reload
        clearCartItemsDisplay();
        updateCartDisplay({
            cart_count: 0,
            cart_total: 0,
            cart_tax: 0,
            cart_final_total: 0
        });
        
        // Hide success modal
        document.getElementById('success-modal').classList.add('hidden');
        
        // Show notification
        showNotification('Ready for new sale', 'success');
    });

    // Helper function to refresh cart items via AJAX
    function refreshCartItems() {
        fetch('/pos/', {
            method: 'GET',
            headers: {
                'X-CSRFToken': csrftoken,
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.text())
        .then(html => {
            // Parse the returned HTML and update cart section
            const parser = new DOMParser();
            const doc = parser.parseFromString(html, 'text/html');
            const newCartItems = doc.querySelector('#cart-items');
            
            if (newCartItems) {
                const currentCartItems = document.getElementById('cart-items');
                if (currentCartItems) {
                    // Smooth transition
                    currentCartItems.style.opacity = '0.5';
                    setTimeout(() => {
                        currentCartItems.innerHTML = newCartItems.innerHTML;
                        currentCartItems.style.opacity = '1';
                    }, 150);
                }
            }
        })
        .catch(error => {
            console.error('Error refreshing cart items:', error);
        });
    }

    // Helper function to clear cart items display
    function clearCartItemsDisplay() {
        const cartItems = document.getElementById('cart-items');
        if (cartItems) {
            // Smooth fade out
            cartItems.style.opacity = '0.5';
            setTimeout(() => {
                cartItems.innerHTML = '<div class="text-center py-8 text-gray-500">Cart is empty</div>';
                cartItems.style.opacity = '1';
            }, 150);
        }
    }

    // Notification system
    function showNotification(message, type) {
        const notification = document.createElement('div');
        notification.className = `fixed top-4 right-4 z-50 p-4 rounded-lg shadow-lg ${
            type === 'success' ? 'bg-green-600 text-white' : 'bg-red-600 text-white'
        }`;
        notification.innerHTML = `
            <div class="flex items-center space-x-2">
                <i class="fas fa-${type === 'success' ? 'check' : 'exclamation-triangle'}"></i>
                <span>${message}</span>
                <button class="ml-4" onclick="this.parentElement.parentElement.remove()">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.remove();
        }, 5000);
    }

    // Keyboard shortcuts
    document.addEventListener('keydown', function(e) {
        // F1 - Focus search
        if (e.key === 'F1') {
            e.preventDefault();
            productSearch.focus();
        }
        
        // F2 - Checkout
        if (e.key === 'F2' && !checkoutBtn.disabled) {
            e.preventDefault();
            checkoutBtn.click();
        }
        
        // ESC - Close modals
        if (e.key === 'Escape') {
            checkoutModal.classList.add('hidden');
            successModal.classList.add('hidden');
        }
    });
});
