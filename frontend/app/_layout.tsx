import React from 'react';
import { Stack } from 'expo-router';
import { StatusBar } from 'expo-status-bar';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AuthProvider } from '../src/context/AuthContext';
import { CartProvider } from '../src/context/CartContext';

const queryClient = new QueryClient();

export default function RootLayout() {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <CartProvider>
          <StatusBar style="light" />
          <Stack
            screenOptions={{
              headerShown: false,
              contentStyle: { backgroundColor: '#1A1A2E' },
            }}
          >
            <Stack.Screen name="(tabs)" options={{ headerShown: false }} />
            <Stack.Screen name="auth-callback" options={{ headerShown: false }} />
            <Stack.Screen name="product/[id]" options={{ headerShown: false }} />
            <Stack.Screen name="payment-success" options={{ headerShown: false }} />
          </Stack>
        </CartProvider>
      </AuthProvider>
    </QueryClientProvider>
  );
}
