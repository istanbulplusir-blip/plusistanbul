// Debug script for cart items
// Run this in browser console

console.log('=== Cart Debug ===');

// Check localStorage cart
const cartData = localStorage.getItem('cart');
console.log('Cart data from localStorage:', cartData);

if (cartData) {
  try {
    const cart = JSON.parse(cartData);
    console.log('Parsed cart:', cart);
    
    if (cart.items && cart.items.length > 0) {
      console.log('Cart items:');
      cart.items.forEach((item, index) => {
        console.log(`Item ${index + 1}:`, {
          id: item.id,
          type: item.type,
          title: item.title,
          tour_id: item.tour_id,
          schedule_id: item.schedule_id,
          variant_id: item.variant_id,
          participants: item.participants,
          selected_options: item.selected_options
        });
      });
    } else {
      console.log('No items in cart');
    }
  } catch (e) {
    console.error('Error parsing cart data:', e);
  }
}

// Check if we have any cart items in memory
if (typeof window !== 'undefined' && window.__NEXT_DATA__) {
  console.log('Next.js data available');
}

console.log('=== End Cart Debug ==='); 