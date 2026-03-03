import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  ActivityIndicator,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import { useRouter } from 'expo-router';
import { useQuery } from '@tanstack/react-query';
import { api } from '../src/services/api';
import { useAuth } from '../src/context/AuthContext';

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

export default function OrdersScreen() {
  const router = useRouter();
  const { isAuthenticated } = useAuth();

  const { data: orders, isLoading } = useQuery({
    queryKey: ['orders'],
    queryFn: api.getOrders,
    enabled: isAuthenticated,
  });

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'paid': return COLORS.success;
      case 'shipped': return '#2196F3';
      case 'delivered': return COLORS.gold;
      case 'cancelled': return COLORS.accent;
      default: return COLORS.gray;
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'pending': return 'Pendiente';
      case 'paid': return 'Pagado';
      case 'shipped': return 'Enviado';
      case 'delivered': return 'Entregado';
      case 'cancelled': return 'Cancelado';
      default: return status;
    }
  };

  if (!isAuthenticated) {
    return (
      <SafeAreaView style={styles.container} edges={['top']}>
        <View style={styles.header}>
          <TouchableOpacity style={styles.backBtn} onPress={() => router.back()}>
            <Ionicons name="arrow-back" size={24} color={COLORS.white} />
          </TouchableOpacity>
          <Text style={styles.headerTitle}>Mis Pedidos</Text>
          <View style={{ width: 44 }} />
        </View>
        <View style={styles.emptyContainer}>
          <Ionicons name="log-in-outline" size={60} color={COLORS.gray} />
          <Text style={styles.emptyText}>Inicia sesión para ver tus pedidos</Text>
        </View>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.container} edges={['top']}>
      <View style={styles.header}>
        <TouchableOpacity style={styles.backBtn} onPress={() => router.back()}>
          <Ionicons name="arrow-back" size={24} color={COLORS.white} />
        </TouchableOpacity>
        <Text style={styles.headerTitle}>Mis Pedidos</Text>
        <View style={{ width: 44 }} />
      </View>

      <View style={styles.content}>
        {isLoading ? (
          <View style={styles.loadingContainer}>
            <ActivityIndicator size="large" color={COLORS.accent} />
          </View>
        ) : !orders || orders.length === 0 ? (
          <View style={styles.emptyContainer}>
            <Ionicons name="receipt-outline" size={60} color={COLORS.gray} />
            <Text style={styles.emptyText}>No tienes pedidos aún</Text>
            <TouchableOpacity
              style={styles.shopBtn}
              onPress={() => router.push('/(tabs)')}
            >
              <Text style={styles.shopBtnText}>Explorar productos</Text>
            </TouchableOpacity>
          </View>
        ) : (
          <ScrollView showsVerticalScrollIndicator={false}>
            {orders.map((order: any) => (
              <View key={order.order_id} style={styles.orderCard}>
                <View style={styles.orderHeader}>
                  <View>
                    <Text style={styles.orderNumber}>Pedido #{order.order_id.slice(-8)}</Text>
                    <Text style={styles.orderDate}>
                      {new Date(order.created_at).toLocaleDateString('es-ES', {
                        year: 'numeric',
                        month: 'long',
                        day: 'numeric',
                      })}
                    </Text>
                  </View>
                  <View style={[styles.statusBadge, { backgroundColor: getStatusColor(order.status) + '20' }]}>
                    <Text style={[styles.statusText, { color: getStatusColor(order.status) }]}>
                      {getStatusText(order.status)}
                    </Text>
                  </View>
                </View>

                <View style={styles.orderItems}>
                  {order.items.slice(0, 2).map((item: any, index: number) => (
                    <Text key={index} style={styles.orderItem} numberOfLines={1}>
                      {item.quantity}x {item.title}
                    </Text>
                  ))}
                  {order.items.length > 2 && (
                    <Text style={styles.moreItems}>
                      +{order.items.length - 2} productos más
                    </Text>
                  )}
                </View>

                <View style={styles.orderFooter}>
                  <Text style={styles.orderTotal}>€{order.total.toFixed(2)}</Text>
                  <TouchableOpacity
                    style={styles.detailsBtn}
                    onPress={() => router.push(`/order/${order.order_id}`)}
                  >
                    <Text style={styles.detailsBtnText}>Ver detalles</Text>
                    <Ionicons name="chevron-forward" size={16} color={COLORS.accent} />
                  </TouchableOpacity>
                </View>
              </View>
            ))}
            <View style={{ height: 100 }} />
          </ScrollView>
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
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 16,
    paddingVertical: 12,
  },
  backBtn: {
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: 'rgba(255,255,255,0.1)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  headerTitle: {
    fontSize: 20,
    fontWeight: '700',
    color: COLORS.white,
  },
  content: {
    flex: 1,
    backgroundColor: COLORS.lightGray,
    borderTopLeftRadius: 24,
    borderTopRightRadius: 24,
    paddingTop: 20,
    paddingHorizontal: 16,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 40,
  },
  emptyText: {
    fontSize: 16,
    color: COLORS.gray,
    marginTop: 16,
    textAlign: 'center',
  },
  shopBtn: {
    backgroundColor: COLORS.accent,
    paddingHorizontal: 24,
    paddingVertical: 12,
    borderRadius: 12,
    marginTop: 20,
  },
  shopBtnText: {
    color: COLORS.white,
    fontSize: 16,
    fontWeight: '600',
  },
  orderCard: {
    backgroundColor: COLORS.white,
    borderRadius: 16,
    padding: 16,
    marginBottom: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.05,
    shadowRadius: 8,
    elevation: 2,
  },
  orderHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 12,
  },
  orderNumber: {
    fontSize: 16,
    fontWeight: '700',
    color: COLORS.text,
  },
  orderDate: {
    fontSize: 13,
    color: COLORS.gray,
    marginTop: 2,
  },
  statusBadge: {
    paddingHorizontal: 12,
    paddingVertical: 4,
    borderRadius: 12,
  },
  statusText: {
    fontSize: 12,
    fontWeight: '600',
  },
  orderItems: {
    borderTopWidth: 1,
    borderTopColor: '#F0F0F0',
    paddingTop: 12,
    marginBottom: 12,
  },
  orderItem: {
    fontSize: 14,
    color: COLORS.text,
    marginBottom: 4,
  },
  moreItems: {
    fontSize: 13,
    color: COLORS.gray,
    fontStyle: 'italic',
  },
  orderFooter: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    borderTopWidth: 1,
    borderTopColor: '#F0F0F0',
    paddingTop: 12,
  },
  orderTotal: {
    fontSize: 20,
    fontWeight: '700',
    color: COLORS.accent,
  },
  detailsBtn: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
  },
  detailsBtnText: {
    fontSize: 14,
    color: COLORS.accent,
    fontWeight: '600',
  },
});
