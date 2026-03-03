import React from 'react';
import { Tabs } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { View, StyleSheet } from 'react-native';
import { useCart } from '../../src/context/CartContext';

const COLORS = {
  primary: '#1A1A2E',
  accent: '#E94560',
  gold: '#D4AF37',
  white: '#FFFFFF',
  gray: '#8E8E93',
};

export default function TabsLayout() {
  const { itemCount } = useCart();

  return (
    <Tabs
      screenOptions={{
        headerShown: false,
        tabBarStyle: styles.tabBar,
        tabBarActiveTintColor: COLORS.accent,
        tabBarInactiveTintColor: COLORS.gray,
        tabBarLabelStyle: styles.tabLabel,
      }}
    >
      <Tabs.Screen
        name="index"
        options={{
          title: 'Inicio',
          tabBarIcon: ({ color, size }) => (
            <Ionicons name="home" size={size} color={color} />
          ),
        }}
      />
      <Tabs.Screen
        name="categories"
        options={{
          title: 'Categorías',
          tabBarIcon: ({ color, size }) => (
            <Ionicons name="grid" size={size} color={color} />
          ),
        }}
      />
      <Tabs.Screen
        name="cart"
        options={{
          title: 'Carrito',
          tabBarIcon: ({ color, size }) => (
            <View>
              <Ionicons name="cart" size={size} color={color} />
              {itemCount > 0 && (
                <View style={styles.badge}>
                  <Ionicons name="ellipse" size={18} color={COLORS.accent} />
                </View>
              )}
            </View>
          ),
        }}
      />
      <Tabs.Screen
        name="profile"
        options={{
          title: 'Perfil',
          tabBarIcon: ({ color, size }) => (
            <Ionicons name="person" size={size} color={color} />
          ),
        }}
      />
    </Tabs>
  );
}

const styles = StyleSheet.create({
  tabBar: {
    backgroundColor: COLORS.primary,
    borderTopColor: 'rgba(255,255,255,0.1)',
    borderTopWidth: 1,
    paddingTop: 8,
    paddingBottom: 8,
    height: 70,
  },
  tabLabel: {
    fontSize: 11,
    fontWeight: '600',
  },
  badge: {
    position: 'absolute',
    right: -8,
    top: -4,
  },
});
