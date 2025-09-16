// Test JavaScript file
console.log('TEST: This file is loading correctly!');
alert('JavaScript is working!');

document.addEventListener('DOMContentLoaded', function() {
    console.log('TEST: DOM is ready');
    
    // Find checkout button
    const btn = document.getElementById('checkout-btn');
    if (btn) {
        console.log('TEST: Found checkout button');
        btn.addEventListener('click', function() {
            alert('Checkout button clicked!');
        });
    } else {
        console.log('TEST: Checkout button NOT found');
    }
});