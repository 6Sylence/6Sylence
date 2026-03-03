import React, { createContext, useContext, useState, useEffect, useCallback, ReactNode } from 'react';
import { api } from '../services/api';
import { useAuth } from './AuthContext';

interface CartItem {
  product_id: string;
  title: string;
  price: number;
  image?: string;
  quantity: number;
  item_total: number;
  stock: number;
}

interface Cart {
  items: CartItem[];
  total: number;
}

interface CartContextType {
  cart: Cart | null;
  loading: boolean;
  itemCount: number;
  addToCart: (productId: string, quantity?: number) => Promise<void>;
  updateQuantity: (productId: string, quantity: number) => Promise<void>;
  removeItem: (productId: string) => Promise<void>;
  clearCart: () => Promise<void>;
  refetch: () => Promise<void>;
}

const CartContext = createContext<CartContextType | undefined>(undefined);

export function CartProvider({ children }: { children: ReactNode }) {
  const { isAuthenticated } = useAuth();
  const [cart, setCart] = useState<Cart | null>(null);
  const [loading, setLoading] = useState(false);

  const fetchCart = useCallback(async () => {
    if (!isAuthenticated) {
      setCart(null);
      return;
    }

    setLoading(true);
    try {
      const cartData = await api.getCart();
      setCart(cartData);
    } catch (error) {
      console.error('Error fetching cart:', error);
      setCart({ items: [], total: 0 });
    } finally {
      setLoading(false);
    }
  }, [isAuthenticated]);

  useEffect(() => {
    fetchCart();
  }, [fetchCart]);

  const addToCart = async (productId: string, quantity: number = 1) => {
    try {
      await api.addToCart(productId, quantity);
      await fetchCart();
    } catch (error) {
      throw error;
    }
  };

  const updateQuantity = async (productId: string, quantity: number) => {
    try {
      await api.updateCartItem(productId, quantity);
      await fetchCart();
    } catch (error) {
      throw error;
    }
  };

  const removeItem = async (productId: string) => {
    try {
      await api.updateCartItem(productId, 0);
      await fetchCart();
    } catch (error) {
      throw error;
    }
  };

  const clearCart = async () => {
    try {
      await api.clearCart();
      setCart({ items: [], total: 0 });
    } catch (error) {
      throw error;
    }
  };

  const itemCount = cart?.items?.reduce((sum, item) => sum + item.quantity, 0) || 0;

  return (
    <CartContext.Provider
      value={{
        cart,
        loading,
        itemCount,
        addToCart,
        updateQuantity,
        removeItem,
        clearCart,
        refetch: fetchCart,
      }}
    >
      {children}
    </CartContext.Provider>
  );
}

export function useCart() {
  const context = useContext(CartContext);
  if (context === undefined) {
    throw new Error('useCart must be used within a CartProvider');
  }
  return context;
}
