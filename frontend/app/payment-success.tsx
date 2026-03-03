import React, { useEffect, useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ActivityIndicator,
  TouchableOpacity,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import { useRouter, useLocalSearchParams } from 'expo-router';
import { api } from '../src/services/api';
import { useCart } from '../src/context/CartContext';

const COLORS = {
  primary: '#1A1A2E',
  accent: '#E94560',
  gold: '#D4AF37',
  white: '#FFFFFF',
  lightGray: '#F5F5F5',
  success: '#4CAF50',
  text: '#333333',
};

export default function PaymentSuccessScreen() {
  const router = useRouter();
  const { session_id } = useLocalSearchParams<{ session_id: string }>();
  const { refetch } = useCart();
  const [status, setStatus] = useState<'loading' | 'success' | 'error'>('loading');
  const [orderId, setOrderId] = useState<string | null>(null);
  const [attempts, setAttempts] = useState(0);

  useEffect(() => {
    if (!session_id) {
      setStatus('error');
      return;
    }

    const checkStatus = async () => {
      try {
        const result = await api.getCheckoutStatus(session_id);
        
        if (result.status === 'paid') {
          setStatus('success');
          setOrderId(result.order_id);
          await refetch(); // Clear cart
        } else if (result.status === 'expired') {
          setStatus('error');
        } else if (attempts < 5) {
          // Still pending, poll again
          setTimeout(() => setAttempts(a => a + 1), 2000);
        } else {
          setStatus('error');
        }
      } catch (error) {
        console.error('Error checking payment status:', error);
        if (attempts < 5) {
          setTimeout(() => setAttempts(a => a + 1), 2000);
        } else {
          setStatus('error');
        }
      }
    };

    checkStatus();
  }, [session_id, attempts]);

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.content}>
        {status === 'loading' && (
          <>
            <ActivityIndicator size="large" color={COLORS.accent} />
            <Text style={styles.loadingText}>Verificando pago...</Text>
          </>
        )}

        {status === 'success' && (
          <>
            <View style={styles.successIcon}>
              <Ionicons name="checkmark-circle" size={100} color={COLORS.success} />
            </View>
            <Text style={styles.successTitle}>¡Pago completado!</Text>
            <Text style={styles.successSubtitle}>
              Tu pedido ha sido procesado correctamente
            </Text>
            {orderId && (
              <View style={styles.orderInfo}>
                <Text style={styles.orderLabel}>Número de pedido:</Text>
                <Text style={styles.orderId}>{orderId}</Text>
              </View>
            )}
            <TouchableOpacity
              style={styles.primaryBtn}
              onPress={() => router.push('/orders')}
            >
              <Text style={styles.primaryBtnText}>Ver mis pedidos</Text>
            </TouchableOpacity>
            <TouchableOpacity
              style={styles.secondaryBtn}
              onPress={() => router.push('/(tabs)')}
            >
              <Text style={styles.secondaryBtnText}>Seguir comprando</Text>
            </TouchableOpacity>
          </>
        )}

        {status === 'error' && (
          <>
            <View style={styles.errorIcon}>
              <Ionicons name="close-circle" size={100} color={COLORS.accent} />
            </View>
            <Text style={styles.errorTitle}>Error en el pago</Text>
            <Text style={styles.errorSubtitle}>
              No se pudo completar el pago. Por favor, inténtalo de nuevo.
            </Text>
            <TouchableOpacity
              style={styles.primaryBtn}
              onPress={() => router.push('/(tabs)/cart')}
            >
              <Text style={styles.primaryBtnText}>Volver al carrito</Text>
            </TouchableOpacity>
          </>
        )}
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: COLORS.lightGray,
  },
  content: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 32,
  },
  loadingText: {
    fontSize: 18,
    color: COLORS.text,
    marginTop: 20,
  },
  successIcon: {
    marginBottom: 24,
  },
  successTitle: {
    fontSize: 28,
    fontWeight: '700',
    color: COLORS.text,
    textAlign: 'center',
  },
  successSubtitle: {
    fontSize: 16,
    color: COLORS.text,
    textAlign: 'center',
    marginTop: 8,
    opacity: 0.7,
  },
  orderInfo: {
    backgroundColor: COLORS.white,
    borderRadius: 12,
    padding: 16,
    marginTop: 24,
    alignItems: 'center',
  },
  orderLabel: {
    fontSize: 14,
    color: COLORS.text,
    opacity: 0.7,
  },
  orderId: {
    fontSize: 18,
    fontWeight: '600',
    color: COLORS.primary,
    marginTop: 4,
  },
  primaryBtn: {
    backgroundColor: COLORS.accent,
    paddingHorizontal: 32,
    paddingVertical: 16,
    borderRadius: 12,
    marginTop: 32,
    width: '100%',
  },
  primaryBtnText: {
    color: COLORS.white,
    fontSize: 16,
    fontWeight: '700',
    textAlign: 'center',
  },
  secondaryBtn: {
    paddingHorizontal: 32,
    paddingVertical: 16,
    marginTop: 12,
  },
  secondaryBtnText: {
    color: COLORS.accent,
    fontSize: 16,
    fontWeight: '600',
  },
  errorIcon: {
    marginBottom: 24,
  },
  errorTitle: {
    fontSize: 28,
    fontWeight: '700',
    color: COLORS.text,
    textAlign: 'center',
  },
  errorSubtitle: {
    fontSize: 16,
    color: COLORS.text,
    textAlign: 'center',
    marginTop: 8,
    opacity: 0.7,
  },
});
