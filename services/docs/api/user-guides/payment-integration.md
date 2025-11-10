# Intégration de Paiement

## Stripe
```javascript
const stripe = require('stripe')('sk_test_...');

const paymentIntent = await stripe.paymentIntents.create({
  amount: 2000,
  currency: 'usd',
});