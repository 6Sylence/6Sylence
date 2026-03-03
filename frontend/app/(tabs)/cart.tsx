import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  ActivityIndicator,
  Alert,
  Platform,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import { useRouter } from 'expo-router';
import { useCart } from '../../src/context/CartContext';
import { useAuth } from '../../src/context/AuthContext';
import { api } from '../../src/services/api';
import * as WebBrowser from 'expo-web-browser';
import * as Linking from 'expo-linking';

const COLORS = {
  primary: '#1A1A2E',
  accent: '#E94560',
  gold: '#D4AF37',
  white: '#FFFFFF',
  lightGray: '#F5F5F5',
  gray: '#8E8E93',
  text: '#333333',
  success: '#4CAF50',
};

export default function CartScreen() {
  const router = useRouter();
  const { user, isAuthenticated, login } = useAuth();
  const { cart, loading, updateQuantity, removeItem, refetch } = useCart();
  const [checkingOut, setCheckingOut] = useState(false);

  const handleCheckout = async () => {
    if (!isAuthenticated) {
      Alert.alert(
        'Inicia sesión',
        'Necesitas iniciar sesión para continuar con la compra',
        [
          { text: 'Cancelar', style: 'cancel' },
          { text: 'Iniciar sesión', onPress: login },
        ]
      );
      return;
    }

    if (!cart?.items || cart.items.length === 0) {
      Alert.alert('Carrito vacío', 'Añade productos a tu carrito antes de continuar');
      return;
    }

    setCheckingOut(true);
    try {
      const originUrl = Linking.createURL('');
      const response = await api.createCheckoutSession(originUrl);
      
      if (response.checkout_url) {
        // Open Stripe checkout in browser
        const result = await WebBrowser.openBrowserAsync(response.checkout_url);
        
        // After returning, refresh cart
        await refetch();
      }
    } catch (error: any) {
      console.error('Checkout error:', error);
      Alert.alert('Error', error.message || 'No se pudo procesar el pago');
    } finally {
      setCheckingOut(false);
    }
  };

  if (loading) {
    return (
      <SafeAreaView style={styles.container} edges={['top']}>
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color={COLORS.accent} />
        </View>
      </SafeAreaView>
    );
  }

  const isEmpty = !cart?.items || cart.items.length === 0;

  return (
    <SafeAreaView style={styles.container} edges={['top']}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Mi Carrito</Text>
        <Text style={styles.headerSubtitle}>
          {isEmpty ? 'Está vacío' : `${cart.items.length} producto${cart.items.length > 1 ? 's' : ''}`}
        </Text>
      </View>

      <View style={styles.content}>
        {isEmpty ? (
          <View style={styles.emptyContainer}>
            <Ionicons name="cart-outline" size={80} color={COLORS.gray} />
            <Text style={styles.emptyTitle}>Tu carrito está vacío</Text>
            <Text style={styles.emptySubtitle}>Explora nuestros productos y añade los que te gusten</Text>
            <TouchableOpacity style={styles.shopButton} onPress={() => router.push('/(tabs)')}>
              <Text style={styles.shopButtonText}>Explorar productos</Text>
            </TouchableOpacity>
          </View>
        ) : (
          <>
            <ScrollView style={styles.itemsList} showsVerticalScrollIndicator={false}>
              {cart.items.map((item: any) => (
                <View key={item.product_id} style={styles.cartItem}>
                  <View style={styles.itemImagePlaceholder}>
                    <Ionicons name="cube-outline" size={32} color={COLORS.gray} />
                  </View>
                  <View style={styles.itemInfo}>
                    <Text style={styles.itemTitle} numberOfLines={2}>{item.title}</Text>
                    <Text style={styles.itemPrice}>€{item.price.toFixed(2)}</Text>
                  </View>
                  <View style={styles.quantityContainer}>
                    <TouchableOpacity
                      style={styles.quantityBtn}
                      onPress={() => {
                        if (item.quantity <= 1) {
                          removeItem(item.product_id);
                        } else {
                          updateQuantity(item.product_id, item.quantity - 1);
                        }
                      }}
                    >
                      <Ionicons name="remove" size={18} color={COLORS.text} />
                    </TouchableOpacity>
                    <Text style={styles.quantity}>{item.quantity}</Text>
                    <TouchableOpacity
                      style={styles.quantityBtn}
                      onPress={() => updateQuantity(item.product_id, item.quantity + 1)}
                    >
                      <Ionicons name="add" size={18} color={COLORS.text} />
                    </TouchableOpacity>
                  </View>
                  <TouchableOpacity
                    style={styles.removeBtn}
                    onPress={() => removeItem(item.product_id)}
                  >
                    <Ionicons name="trash-outline" size={20} color={COLORS.accent} />
                  </TouchableOpacity>
                </View>
              ))}
              <View style={{ height: 200 }} />
            </ScrollView>

            {/* Checkout Footer */}
            <View style={styles.checkoutFooter}>
              <View style={styles.totalContainer}>
                <Text style={styles.totalLabel}>Total</Text>
                <Text style={styles.totalAmount}>€{cart.total.toFixed(2)}</Text>
              </View>
              <TouchableOpacity
                style={[styles.checkoutBtn, checkingOut && styles.checkoutBtnDisabled]}
                onPress={handleCheckout}
                disabled={checkingOut}
              >
                {checkingOut ? (
                  <ActivityIndicator color={COLORS.white} />
                ) : (
                  <>
                    <Ionicons name="lock-closed" size={20} color={COLORS.white} />
                    <Text style={styles.checkoutBtnText}>Pagar ahora</Text>
                  </>
                )}
              </TouchableOpacity>
            </View>
          </>
        )}
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: COLORS.primary,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  header: {
    paddingHorizontal: 16,
    paddingVertical: 20,
  },
  headerTitle: {
    fontSize: 28,
    fontWeight: '700',
    color: COLORS.white,
  },
  headerSubtitle: {
    fontSize: 14,
    color: COLORS.gold,
    marginTop: 4,
  },
  content: {
    flex: 1,
    backgroundColor: COLORS.lightGray,
    borderTopLeftRadius: 24,
    borderTopRightRadius: 24,
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 40,
  },
  emptyTitle: {
    fontSize: 20,
    fontWeight: '600',
    color: COLORS.text,
    marginTop: 20,
  },
  emptySubtitle: {
    fontSize: 14,
    color: COLORS.gray,
    textAlign: 'center',
    marginTop: 8,
  },
  shopButton: {
    backgroundColor: COLORS.accent,
    paddingHorizontal: 32,
    paddingVertical: 14,
    borderRadius: 12,
    marginTop: 24,
  },
  shopButtonText: {
    color: COLORS.white,
    fontSize: 16,
    fontWeight: '600',
  },
  itemsList: {
    flex: 1,
    padding: 16,
  },
  cartItem: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: COLORS.white,
    borderRadius: 16,
    padding: 12,
    marginBottom: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.05,
    shadowRadius: 8,
    elevation: 2,
  },
  itemImagePlaceholder: {
    width: 60,
    height: 60,
    borderRadius: 8,
    backgroundColor: COLORS.lightGray,
    justifyContent: 'center',
    alignItems: 'center',
  },
  itemInfo: {
    flex: 1,
    marginLeft: 12,
  },
  itemTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: COLORS.text,
  },
  itemPrice: {
    fontSize: 16,
    fontWeight: '700',
    color: COLORS.accent,
    marginTop: 4,
  },
  quantityContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: COLORS.lightGray,
    borderRadius: 8,
    marginRight: 8,
  },
  quantityBtn: {
    padding: 8,
  },
  quantity: {
    fontSize: 14,
    fontWeight: '600',
    color: COLORS.text,
    minWidth: 24,
    textAlign: 'center',
  },
  removeBtn: {
    padding: 8,
  },
  checkoutFooter: {
    position: 'absolute',
    bottom: 0,
    left: 0,
    right: 0,
    backgroundColor: COLORS.white,
    padding: 16,
    paddingBottom: Platform.OS === 'ios' ? 32 : 16,
    borderTopLeftRadius: 24,
    borderTopRightRadius: 24,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: -4 },
    shadowOpacity: 0.1,
    shadowRadius: 12,
    elevation: 8,
  },
  totalContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
  },
  totalLabel: {
    fontSize: 16,
    color: COLORS.gray,
  },
  totalAmount: {
    fontSize: 24,
    fontWeight: '700',
    color: COLORS.text,
  },
  checkoutBtn: {
    flexDirection: 'row',
    backgroundColor: COLORS.accent,
    borderRadius: 14,
    padding: 16,
    justifyContent: 'center',
    alignItems: 'center',
    gap: 8,
  },
  checkoutBtnDisabled: {
    opacity: 0.7,
  },
  checkoutBtnText: {
    color: COLORS.white,
    fontSize: 18,
    fontWeight: '700',
  },
});
