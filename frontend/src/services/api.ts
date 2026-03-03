import axios from 'axios';
import Constants from 'expo-constants';

const BASE_URL = process.env.EXPO_PUBLIC_BACKEND_URL || '';

const axiosInstance = axios.create({
  baseURL: BASE_URL,
  timeout: 30000,
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const api = {
  // Auth
  exchangeSession: async (sessionId: string) => {
    const response = await axiosInstance.post('/api/auth/session', { session_id: sessionId });
    return response.data;
  },

  getMe: async () => {
    const response = await axiosInstance.get('/api/auth/me');
    return response.data;
  },

  logout: async () => {
    const response = await axiosInstance.post('/api/auth/logout');
    return response.data;
  },

  becomeSeller: async () => {
    const response = await axiosInstance.post('/api/auth/become-seller');
    return response.data;
  },

  // Categories
  getCategories: async () => {
    const response = await axiosInstance.get('/api/categories');
    return response.data;
  },

  // Products
  getProducts: async (params?: {
    category_id?: string;
    search?: string;
    featured?: boolean;
    seller_id?: string;
    limit?: number;
    skip?: number;
  }) => {
    const response = await axiosInstance.get('/api/products', { params });
    return response.data;
  },

  getProduct: async (productId: string) => {
    const response = await axiosInstance.get(`/api/products/${productId}`);
    return response.data;
  },

  createProduct: async (product: {
    title: string;
    description: string;
    price: number;
    original_price?: number;
    category_id: string;
    images?: string[];
    stock?: number;
  }) => {
    const response = await axiosInstance.post('/api/products', product);
    return response.data;
  },

  updateProduct: async (productId: string, updates: any) => {
    const response = await axiosInstance.put(`/api/products/${productId}`, updates);
    return response.data;
  },

  deleteProduct: async (productId: string) => {
    const response = await axiosInstance.delete(`/api/products/${productId}`);
    return response.data;
  },

  // Reviews
  getReviews: async (productId: string) => {
    const response = await axiosInstance.get(`/api/products/${productId}/reviews`);
    return response.data;
  },

  createReview: async (review: { product_id: string; rating: number; comment: string }) => {
    const response = await axiosInstance.post('/api/reviews', review);
    return response.data;
  },

  // Cart
  getCart: async () => {
    const response = await axiosInstance.get('/api/cart');
    return response.data;
  },

  addToCart: async (productId: string, quantity: number = 1) => {
    const response = await axiosInstance.post('/api/cart/add', {
      product_id: productId,
      quantity,
    });
    return response.data;
  },

  updateCartItem: async (productId: string, quantity: number) => {
    const response = await axiosInstance.post('/api/cart/update', {
      product_id: productId,
      quantity,
    });
    return response.data;
  },

  clearCart: async () => {
    const response = await axiosInstance.delete('/api/cart/clear');
    return response.data;
  },

  // Checkout
  createCheckoutSession: async (originUrl: string) => {
    const response = await axiosInstance.post('/api/checkout/create-session', {
      origin_url: originUrl,
    });
    return response.data;
  },

  getCheckoutStatus: async (sessionId: string) => {
    const response = await axiosInstance.get(`/api/checkout/status/${sessionId}`);
    return response.data;
  },

  // Orders
  getOrders: async () => {
    const response = await axiosInstance.get('/api/orders');
    return response.data;
  },

  getOrder: async (orderId: string) => {
    const response = await axiosInstance.get(`/api/orders/${orderId}`);
    return response.data;
  },

  // Seller
  getSellerProducts: async () => {
    const response = await axiosInstance.get('/api/seller/products');
    return response.data;
  },

  getSellerOrders: async () => {
    const response = await axiosInstance.get('/api/seller/orders');
    return response.data;
  },

  getSellerStats: async () => {
    const response = await axiosInstance.get('/api/seller/stats');
    return response.data;
  },

  // Seed
  seedData: async () => {
    const response = await axiosInstance.post('/api/seed');
    return response.data;
  },
};
