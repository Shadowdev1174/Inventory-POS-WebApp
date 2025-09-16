// Simple, Fast POS JavaScript - No Flickering
document.addEventListener('DOMContentLoaded', function() {
    console.log('POS JavaScript loaded successfully!');
    
    // Set current date and time
    function setCurrentDateTime() {
        const now = new Date();
        
        // Date formatting
        const dateOptions = { 
            year: 'numeric', 
            month: 'short', 
            day: 'numeric',
            timeZone: 'Asia/Manila' // Philippines timezone
        };
        const formattedDate = now.toLocaleDateString('en-US', dateOptions);
        
        // Time formatting
        const timeOptions = {
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit',
            timeZone: 'Asia/Manila',
            hour12: true
        };
        const formattedTime = now.toLocaleTimeString('en-US', timeOptions);
        
        // Update elements
        const dateElement = document.getElementById('current-date');
        const timeElement = document.getElementById('current-time');
        
        if (dateElement) {
            dateElement.textContent = formattedDate;
        }
        
        if (timeElement) {
            timeElement.textContent = formattedTime;
        }
    }
    
    // Set date/time immediately and update every second
    setCurrentDateTime();
    setInterval(setCurrentDateTime, 1000); // Update every second
    
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

    // Simple toast notification
    function showToast(message, type = 'success') {
        const toast = document.createElement('div');
        toast.className = `fixed top-4 right-4 z-50 p-3 rounded shadow-lg text-white ${
            type === 'success' ? 'bg-green-500' : 'bg-red-500'
        }`;
        toast.textContent = message;
        document.body.appendChild(toast);
        setTimeout(() => toast.remove(), 2000);
    }

    // Update cart display instantly
    function updateCartNumbers(data) {
        const elements = {
            'cart-count': data.cart_count || 0,
            'cart-subtotal': `₱${(data.cart_total || 0).toFixed(2)}`,
            'cart-tax': `₱${(data.cart_tax || 0).toFixed(2)}`,
            'cart-total': `₱${(data.cart_final_total || 0).toFixed(2)}`
        };

        Object.keys(elements).forEach(id => {
            const el = document.getElementById(id);
            if (el) el.textContent = elements[id];
        });

        // Enable/disable buttons
        const hasItems = (data.cart_count || 0) > 0;
        ['checkout-btn', 'clear-cart-btn'].forEach(id => {
            const btn = document.getElementById(id);
            if (btn) btn.disabled = !hasItems;
        });
    }

    // Simple AJAX request
    async function quickRequest(url, data = null) {
        try {
            const response = await fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrftoken,
                },
                body: data ? JSON.stringify(data) : null
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const result = await response.json();
            console.log(`Request to ${url}:`, result); // Debug log
            return result;
        } catch (error) {
            console.error(`Error in request to ${url}:`, error);
            showToast('Operation failed: ' + error.message, 'error');
            return { status: 'error', message: error.message };
        }
    }

    // Event delegation for all clicks
    document.addEventListener('click', async function(e) {
        // Add to cart
        const productCard = e.target.closest('.product-card');
        if (productCard && productCard.dataset.productId) {
            const result = await quickRequest('/pos/add-to-cart/', {
                product_id: productCard.dataset.productId,
                quantity: 1
            });
            if (result?.status === 'success') {
                updateCartNumbers(result);
                showToast('Added to cart');
                // NO PAGE RELOAD - Update cart items via AJAX
                updateCartItemsDisplay();
            }
            return;
        }

        // Checkout
        if (e.target.id === 'checkout-btn') {
            console.log('Checkout button clicked!');
            
            // Check if button is disabled
            if (e.target.disabled) {
                console.log('Checkout button is disabled - cart might be empty');
                showToast('Add items to cart first', 'error');
                return;
            }
            
            const total = document.getElementById('cart-total').textContent;
            console.log('Cart total:', total);
            
            document.getElementById('checkout-total').textContent = total;
            document.getElementById('checkout-modal').classList.remove('hidden');
            console.log('Checkout modal opened');
            return;
        }

        // Clear cart
        if (e.target.id === 'clear-cart-btn') {
            document.getElementById('clear-cart-modal').classList.remove('hidden');
            return;
        }

        // Modal controls
        if (e.target.id === 'cancel-checkout') {
            document.getElementById('checkout-modal').classList.add('hidden');
        }
        
        // Clear cart modal controls
        if (e.target.id === 'cancel-clear-cart') {
            document.getElementById('clear-cart-modal').classList.add('hidden');
        }
        
        if (e.target.id === 'confirm-clear-cart') {
            document.getElementById('clear-cart-modal').classList.add('hidden');
            // Proceed with clearing the cart
            clearCartNow();
        }
        
        // Close modal when clicking outside
        if (e.target.id === 'clear-cart-modal') {
            document.getElementById('clear-cart-modal').classList.add('hidden');
        }

        if (e.target.id === 'new-sale') {
            // Clear everything without page reload
            updateCartNumbers({cart_count: 0, cart_total: 0, cart_tax: 0, cart_final_total: 0});
            const cartItems = document.getElementById('cart-items');
            if (cartItems) {
                cartItems.innerHTML = '<div class="text-center py-8 text-gray-500">Cart is empty</div>';
            }
            document.getElementById('success-modal').classList.add('hidden');
            showToast('Ready for new sale');
        }

        // Cart quantity controls
        if (e.target.classList.contains('quantity-btn')) {
            const cartId = e.target.dataset.cartId;
            const action = e.target.dataset.action;
            
            // Prevent multiple rapid clicks
            if (e.target.disabled) {
                console.log('Button already processing...');
                return;
            }
            
            if (cartId && action) {
                await updateCartQuantity(cartId, action, e.target);
            }
            return;
        }

        // Remove from cart
        if (e.target.classList.contains('remove-item')) {
            const cartId = e.target.dataset.cartId;
            if (cartId && confirm('Remove item?')) {
                await removeFromCart(cartId);
            }
            return;
        }
    });

    // Clear cart function
    async function clearCartNow() {
        try {
            const result = await quickRequest('/pos/clear-cart/');
            if (result?.status === 'success') {
                updateCartNumbers(result);
                showToast('Cart cleared successfully');
                // Clear cart items display without reload
                const cartItems = document.getElementById('cart-items');
                if (cartItems) {
                    cartItems.innerHTML = '<div class="text-center py-8 text-gray-500">Cart is empty</div>';
                }
            }
        } catch (error) {
            console.error('Error clearing cart:', error);
            showToast('Error clearing cart', 'error');
        }
    }

    // Update cart items display via AJAX
    async function updateCartItemsDisplay() {
        try {
            const response = await fetch('/pos/');
            const html = await response.text();
            const parser = new DOMParser();
            const doc = parser.parseFromString(html, 'text/html');
            const newCartItems = doc.querySelector('#cart-items');
            
            if (newCartItems) {
                const currentCartItems = document.getElementById('cart-items');
                if (currentCartItems) {
                    currentCartItems.innerHTML = newCartItems.innerHTML;
                }
            }
        } catch (error) {
            console.error('Error updating cart items:', error);
        }
    }

    // Update cart quantity
    async function updateCartQuantity(cartId, action, buttonElement) {
        const quantityInput = document.querySelector(`input[data-cart-id="${cartId}"]`);
        const quantitySpan = document.querySelector(`[data-cart-id="${cartId}"] .quantity`);
        const allButtons = document.querySelectorAll(`[data-cart-id="${cartId}"].quantity-btn`);
        
        if (!quantityInput) return;

        // Disable all buttons for this cart item to prevent race conditions
        allButtons.forEach(btn => {
            btn.disabled = true;
            btn.style.opacity = '0.5';
        });

        const currentQty = parseInt(quantityInput.value) || 1;
        let newQty = currentQty;

        console.log(`Updating cart ${cartId}: action=${action}, currentQty=${currentQty}`);

        try {
            if (action === 'increase') {
                newQty = currentQty + 1;
            } else if (action === 'decrease') {
                newQty = currentQty - 1;
                // If quantity becomes 0 or less, remove the item
                if (newQty <= 0) {
                    console.log('Quantity is 0, removing item from cart');
                    await removeFromCart(cartId);
                    return;
                }
            }

            console.log(`Sending request to update quantity to ${newQty}`);
            const result = await quickRequest('/pos/update-cart/', {
                cart_id: cartId,
                quantity: newQty
            });

            if (result?.status === 'success') {
                updateCartNumbers(result);
                quantityInput.value = newQty;
                if (quantitySpan) quantitySpan.textContent = newQty;
                showToast('Cart updated');
                console.log(`Successfully updated quantity to ${newQty}`);
            } else {
                showToast(result?.message || 'Update failed', 'error');
                console.error('Cart update failed:', result);
            }
        } catch (error) {
            console.error('Error updating cart quantity:', error);
            showToast('Error updating cart', 'error');
        } finally {
            // Re-enable buttons
            allButtons.forEach(btn => {
                btn.disabled = false;
                btn.style.opacity = '1';
            });
        }
    }

    // Remove from cart
    async function removeFromCart(cartId) {
        console.log(`Removing cart item ${cartId}`);
        
        const cartItem = document.querySelector(`[data-cart-id="${cartId}"]`);
        if (cartItem) {
            cartItem.style.opacity = '0.5'; // Visual feedback
        }

        try {
            const result = await quickRequest('/pos/remove-from-cart/', {
                cart_id: cartId
            });

            if (result?.status === 'success') {
                updateCartNumbers(result);
                // Remove the item from display
                if (cartItem) {
                    cartItem.remove();
                }
                showToast('Item removed');
                console.log(`Successfully removed cart item ${cartId}`);
                // Refresh cart display
                updateCartItemsDisplay();
            } else {
                // Restore opacity if removal failed
                if (cartItem) {
                    cartItem.style.opacity = '1';
                }
                showToast(result?.message || 'Remove failed', 'error');
                console.error('Cart removal failed:', result);
            }
        } catch (error) {
            // Restore opacity if error occurred
            if (cartItem) {
                cartItem.style.opacity = '1';
            }
            console.error('Error removing from cart:', error);
            showToast('Error removing item', 'error');
        }
    }

    // Search functionality
    const searchInput = document.getElementById('product-search');
    if (searchInput) {
        searchInput.addEventListener('input', function(e) {
            const query = e.target.value.toLowerCase();
            document.querySelectorAll('.product-card').forEach(card => {
                const text = card.textContent.toLowerCase();
                card.style.display = text.includes(query) ? 'block' : 'none';
            });
        });
    }

    // Payment handling
    const paymentBtn = document.getElementById('confirm-payment');
    if (paymentBtn) {
        paymentBtn.addEventListener('click', async function() {
            console.log('Payment confirmation clicked!');
            
            const paymentMethod = document.getElementById('payment-method').value;
            const amountReceived = parseFloat(document.getElementById('amount-received').value) || 0;
            const total = parseFloat(document.getElementById('checkout-total').textContent.replace('₱', ''));

            console.log('Payment details:', { paymentMethod, amountReceived, total });

            if (paymentMethod === 'cash' && amountReceived < total) {
                showToast('Insufficient amount', 'error');
                return;
            }

            // Show loading state
            this.disabled = true;
            this.textContent = 'Processing...';

            const result = await quickRequest('/pos/checkout/', {
                payment_method: paymentMethod,
                amount_paid: paymentMethod === 'cash' ? amountReceived : total
            });

            // Reset button
            this.disabled = false;
            this.textContent = 'Confirm Payment';

            console.log('Checkout result:', result); // Debug log

            if (result?.status === 'success') {
                // Show success modal
                document.getElementById('checkout-modal').classList.add('hidden');
                document.getElementById('success-modal').classList.remove('hidden');
                
                // Update success details
                document.getElementById('sale-number').textContent = result.sale_number;
                document.getElementById('sale-total').textContent = `₱${result.total_amount.toFixed(2)}`;
                
                if (result.change_amount > 0) {
                    document.getElementById('sale-change').classList.remove('hidden');
                    document.getElementById('change-given').textContent = `₱${result.change_amount.toFixed(2)}`;
                }
                
                // Clear cart display
                updateCartNumbers({cart_count: 0, cart_total: 0, cart_tax: 0, cart_final_total: 0});
                updateCartItemsDisplay();
            } else {
                // Show error message
                const errorMsg = result?.message || 'Checkout failed. Please try again.';
                showToast(errorMsg, 'error');
                console.error('Checkout error:', result);
            }
        });
    }

    // Amount received input handler
    const amountInput = document.getElementById('amount-received');
    if (amountInput) {
        amountInput.addEventListener('input', function() {
            const total = parseFloat(document.getElementById('checkout-total').textContent.replace('₱', ''));
            const received = parseFloat(this.value) || 0;
            const change = received - total;
            
            const changeDiv = document.getElementById('change-amount');
            if (change >= 0 && changeDiv) {
                changeDiv.classList.remove('hidden');
                changeDiv.querySelector('span').textContent = `₱${change.toFixed(2)}`;
            } else if (changeDiv) {
                changeDiv.classList.add('hidden');
            }
        });
    }
    
    // Direct checkout button handler as backup
    const checkoutButton = document.getElementById('checkout-btn');
    if (checkoutButton) {
        console.log('Checkout button found! Adding direct event listener.');
        checkoutButton.addEventListener('click', function(e) {
            console.log('DIRECT: Checkout button clicked!');
            e.preventDefault();
            
            if (this.disabled) {
                console.log('Button is disabled');
                showToast('Add items to cart first', 'error');
                return;
            }
            
            const total = document.getElementById('cart-total').textContent;
            console.log('Opening checkout modal with total:', total);
            document.getElementById('checkout-total').textContent = total;
            document.getElementById('checkout-modal').classList.remove('hidden');
        });
    } else {
        console.log('ERROR: Checkout button not found!');
    }

    // Category filtering functionality
    const categoryFilters = document.querySelectorAll('.category-filter');
    console.log('Found category filters:', categoryFilters.length);
    
    categoryFilters.forEach(filter => {
        filter.addEventListener('click', function() {
            console.log('Category filter clicked:', this.dataset.category);
            
            // Update active state
            categoryFilters.forEach(f => {
                f.classList.remove('active', 'bg-blue-600', 'text-white');
                f.classList.add('bg-gray-200', 'text-gray-700');
            });
            
            this.classList.add('active', 'bg-blue-600', 'text-white');
            this.classList.remove('bg-gray-200', 'text-gray-700');
            
            // Filter products
            const category = this.dataset.category;
            const productCards = document.querySelectorAll('.product-card');
            console.log(`Filtering products for category: ${category}, found ${productCards.length} product cards`);
            
            let visibleCount = 0;
            productCards.forEach(card => {
                const cardCategory = card.dataset.category;
                // Convert both to strings for comparison and handle uncategorized products
                if (category === 'all' || 
                    String(cardCategory) === String(category) || 
                    (cardCategory === 'uncategorized' && category === 'uncategorized')) {
                    card.style.display = 'block';
                    visibleCount++;
                } else {
                    card.style.display = 'none';
                }
            });
            
            console.log(`Showing ${visibleCount} products for category: ${category}`);
            showToast(`Showing ${visibleCount} product${visibleCount !== 1 ? 's' : ''}`);
        });
    });
});