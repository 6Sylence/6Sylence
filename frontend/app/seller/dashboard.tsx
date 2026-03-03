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
import { api } from '../../src/services/api';
import { useAuth } from '../../src/context/AuthContext';

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

export default function SellerDashboard() {
  const router = useRouter();
  const { user, isAuthenticated } = useAuth();

  const { data: stats, isLoading } = useQuery({
    queryKey: ['seller', 'stats'],
    queryFn: api.getSellerStats,
    enabled: isAuthenticated && user?.role === 'seller',
  });

  if (!isAuthenticated || user?.role !== 'seller') {
    return (
      <SafeAreaView style={styles.container} edges={['top']}>
        <View style={styles.header}>
          <TouchableOpacity style={styles.backBtn} onPress={() => router.back()}>
            <Ionicons name="arrow-back" size={24} color={COLORS.white} />
          </TouchableOpacity>
          <Text style={styles.headerTitle}>Panel de Vendedor</Text>
          <View style={{ width: 44 }} />
        </View>
        <View style={styles.emptyContainer}>
          <Ionicons name="lock-closed-outline" size={60} color={COLORS.gray} />
          <Text style={styles.emptyText}>Debes ser vendedor para acceder aquí</Text>
        </View>
      </SafeAreaView>
    );
  }

  const statCards = [
    { icon: 'cube', label: 'Productos', value: stats?.total_products || 0, color: '#3498db' },
    { icon: 'receipt', label: 'Pedidos', value: stats?.total_orders || 0, color: COLORS.accent },
    { icon: 'cash', label: 'Ingresos', value: `€${stats?.total_revenue?.toFixed(2) || '0.00'}`, color: COLORS.success },
    { icon: 'star', label: 'Valoración', value: stats?.avg_rating?.toFixed(1) || '0.0', color: COLORS.gold },
  ];

  const menuItems = [
    { icon: 'cube-outline', label: 'Mis productos', route: '/seller/products', description: 'Gestiona tu catálogo' },
    { icon: 'add-circle-outline', label: 'Añadir producto', route: '/seller/add-product', description: 'Publica un nuevo producto' },
    { icon: 'receipt-outline', label: 'Pedidos recibidos', route: '/seller/orders', description: 'Ver pedidos de clientes' },
  ];

  return (
    <SafeAreaView style={styles.container} edges={['top']}>
      <View style={styles.header}>
        <TouchableOpacity style={styles.backBtn} onPress={() => router.back()}>
          <Ionicons name="arrow-back" size={24} color={COLORS.white} />
        </TouchableOpacity>
        <Text style={styles.headerTitle}>Panel de Vendedor</Text>
        <View style={{ width: 44 }} />
      </View>

      <ScrollView style={styles.content} showsVerticalScrollIndicator={false}>
        {/* Stats Grid */}
        <View style={styles.statsGrid}>
          {isLoading ? (
            <ActivityIndicator color={COLORS.accent} style={{ padding: 40 }} />
          ) : (
            statCards.map((stat, index) => (
              <View key={index} style={styles.statCard}>
                <View style={[styles.statIcon, { backgroundColor: stat.color + '20' }]}>
                  <Ionicons name={stat.icon as any} size={24} color={stat.color} />
                </View>
                <Text style={styles.statValue}>{stat.value}</Text>
                <Text style={styles.statLabel}>{stat.label}</Text>
              </View>
            ))
          )}
        </View>

        {/* Quick Actions */}
        <Text style={styles.sectionTitle}>Acciones rápidas</Text>
        {menuItems.map((item, index) => (
          <TouchableOpacity
            key={index}
            style={styles.menuItem}
            onPress={() => router.push(item.route as any)}
          >
            <View style={[styles.menuIcon, { backgroundColor: COLORS.gold + '20' }]}>
              <Ionicons name={item.icon as any} size={24} color={COLORS.gold} />
            </View>
            <View style={styles.menuInfo}>
              <Text style={styles.menuLabel}>{item.label}</Text>
              <Text style={styles.menuDescription}>{item.description}</Text>
            </View>
            <Ionicons name="chevron-forward" size={20} color={COLORS.gray} />
          </TouchableOpacity>
        ))}

        <View style={{ height: 100 }} />
      </ScrollView>
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
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 40,
    backgroundColor: COLORS.lightGray,
    borderTopLeftRadius: 24,
    borderTopRightRadius: 24,
  },
  emptyText: {
    fontSize: 16,
    color: COLORS.gray,
    marginTop: 16,
    textAlign: 'center',
  },
  statsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
    marginBottom: 24,
  },
  statCard: {
    width: '48%',
    backgroundColor: COLORS.white,
    borderRadius: 16,
    padding: 16,
    marginBottom: 12,
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.05,
    shadowRadius: 8,
    elevation: 2,
  },
  statIcon: {
    width: 48,
    height: 48,
    borderRadius: 12,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 8,
  },
  statValue: {
    fontSize: 24,
    fontWeight: '700',
    color: COLORS.text,
  },
  statLabel: {
    fontSize: 13,
    color: COLORS.gray,
    marginTop: 2,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '700',
    color: COLORS.text,
    marginBottom: 16,
  },
  menuItem: {
    flexDirection: 'row',
    alignItems: 'center',
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
  menuIcon: {
    width: 48,
    height: 48,
    borderRadius: 12,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 16,
  },
  menuInfo: {
    flex: 1,
  },
  menuLabel: {
    fontSize: 16,
    fontWeight: '600',
    color: COLORS.text,
  },
  menuDescription: {
    fontSize: 13,
    color: COLORS.gray,
    marginTop: 2,
  },
});
