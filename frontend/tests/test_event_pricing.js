// Test script to verify frontend pricing calculation
const testEvent = {
  id: "test-event",
  title: "Test Event",
  pricing_summary: {
    "ticket1": {
      ticket_type_name: "VIP",
      base_price: 100,
      modified_price: 150,
      price_modifier: 1.5
    },
    "ticket2": {
      ticket_type_name: "Standard",
      base_price: 50,
      modified_price: 50,
      price_modifier: 1.0
    }
  },
  min_price: 25,
  ticket_types: [
    { price_modifier: 1.5 },
    { price_modifier: 1.0 },
    { price_modifier: 0.5 }
  ]
};

// Test pricing calculation logic
function calculateMinPrice(event) {
  let minPrice = 0;
  
  // Try pricing_summary first
  if (event.pricing_summary && Object.keys(event.pricing_summary).length > 0) {
    const prices = Object.values(event.pricing_summary).map(p => p.base_price).filter(price => price > 0);
    minPrice = prices.length > 0 ? Math.min(...prices) : 0;
  }
  // Fallback to min_price field if available
  else if (event.min_price && event.min_price > 0) {
    minPrice = event.min_price;
  }
  // Fallback to ticket_types if pricing_summary is not available
  else if (event.ticket_types && event.ticket_types.length > 0) {
    const prices = event.ticket_types.map(t => t.price_modifier * 100).filter(price => price > 0);
    minPrice = prices.length > 0 ? Math.min(...prices) : 0;
  }
  // Default fallback
  else {
    minPrice = 50; // Default minimum price
  }
  
  return minPrice;
}

// Test the calculation
console.log("Testing pricing calculation...");
console.log("Event:", testEvent.title);
console.log("Pricing summary:", testEvent.pricing_summary);
console.log("Calculated min price:", calculateMinPrice(testEvent));

// Test with empty pricing_summary
const testEvent2 = {
  ...testEvent,
  pricing_summary: {}
};
console.log("\nTesting with empty pricing_summary...");
console.log("Calculated min price:", calculateMinPrice(testEvent2));

// Test with no pricing_summary
const testEvent3 = {
  ...testEvent,
  pricing_summary: null
};
console.log("\nTesting with no pricing_summary...");
console.log("Calculated min price:", calculateMinPrice(testEvent3));

console.log("\n✅ Frontend pricing test completed!"); 