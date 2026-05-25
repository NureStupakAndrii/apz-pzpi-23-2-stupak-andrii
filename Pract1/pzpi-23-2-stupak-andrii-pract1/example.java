package org.example;

public class Main {
    public static void main(String[] args) {
        ShoppingCart cart = new ShoppingCart();
        PaymentStrategy paypal = new PayPalStrategy();
        PaymentStrategy card = new CardStrategy();

        cart.setPaymentStrategy(paypal);
        cart.checkout(1);

        cart.setPaymentStrategy(card);
        cart.checkout(5);
    }

    public interface PaymentStrategy {
        void pay(double amount);
    }

    public static class PayPalStrategy implements PaymentStrategy {
        @Override
        public void pay(double amount) {
            System.out.println("Pay " + amount + " via PayPal");
        }
    }

    public static class CardStrategy implements PaymentStrategy {
        @Override
        public void pay(double amount) {
            System.out.println("Pay " + amount + " via Card");
        }
    }

    public static class ShoppingCart {
        private PaymentStrategy paymentStrategy;

        public void setPaymentStrategy(PaymentStrategy strategy) {
            this.paymentStrategy = strategy;
        }

        public void checkout(double amount) {
            paymentStrategy.pay(amount);
        }
    }
}